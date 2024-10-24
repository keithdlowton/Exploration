# %%

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# %%

path_folder = Path("/Users/keithlowton/Desktop/Ks/Python code/Kaggle/IMDB")
print(path_folder.exists())
print(path_folder)


# Load dataset
# data_all = pd.read_csv(os.path.join(path_folder, "data/title.basics.tsv"), sep="\t")

# for name in ["startYear", "endYear", "runtimeMinutes"]:
#     data_all[name][~data_all[name].str.isdigit()] = ""

# data = data_all[(data_all.startYear != "") & (data_all.endYear != "")]
# data = data.sample(n=10000)

# for name in ["startYear", "endYear", "isAdult"]:
#     data[name] = data[name].astype(int)

# data = data[(data.startYear > 1940)]
# data = data.reset_index(drop=True)

# data["duration"] = data.endYear - data.startYear + 1

# print(data.shape)
# data.head()

# data.to_feather(os.path.join(path_folder, "data/data.ftr"))
data = pd.read_feather(os.path.join(path_folder, "data/data.ftr"), columns=None, use_threads=True)
print(data.shape)
data.head()

genre_lst_all = [val for sublist in list(data.genres) for val in sublist]
genre_lst = list(set(genre_lst_all))
genre_lst.remove("\\N")
print(genre_lst)
# for name in genre_lst:
#     lst = []
#     for i in range(data.shape[0]):
#         if name in data.loc[i, "genres"]:
#             lst.append(1)
#         else:
#             lst.append(0)
#     data[name] = lst


# %%
def overview():
    st.subheader("IMDB dataset")
    st.markdown(f"Number of rows in the dataset: {data.shape[0]}", unsafe_allow_html=False)
    st.markdown(f"Years covered, from {min(data.startYear)} to {max(data.startYear)}", unsafe_allow_html=False)
    st.markdown(f"Number of genres: {len(genre_lst)}", unsafe_allow_html=False)
    st.markdown(f"Number of title type: {data.titleType.nunique()}", unsafe_allow_html=False)
    st.markdown(
        f"Number of adult films: {data[data.isAdult == 1].shape[0]} ({data[data.isAdult == 1].shape[0]/data.shape[0]*100:.2f}%)",
        unsafe_allow_html=False,
    )


# %%
def title_type_counts():
    st.subheader("IMDB name titles by year range (Choose Range)")
    year_filter = st.slider(
        "Year Range",
        (data["startYear"].min()),
        (data["startYear"].max()),
        ((data["startYear"].min()), int(data["startYear"].max())),
    )
    filtered_data = data[(data["startYear"] >= year_filter[0]) & (data["startYear"] <= year_filter[1])]
    medal_counts = filtered_data.groupby(["startYear", "titleType"]).size().to_frame("Count").reset_index()
    fig = px.bar(
        medal_counts,
        x="startYear",
        y="Count",
        color="titleType",
        title="Film counts by title type",
        labels={"startYear": "Start year", "titleType": "Title type"},
        hover_data={"startYear": True, "titleType": True, "Count": True},
        color_discrete_sequence=px.colors.qualitative.Prism,
    )
    fig.update_layout(showlegend=True, height=600)
    st.plotly_chart(fig)


# %%
def title_type_stats():
    st.subheader("IMDB name title duration by year range (Choose Range)")
    year_filter = st.slider(
        "Year Range",
        (data["startYear"].min()),
        (data["startYear"].max()),
        ((data["startYear"].min()), int(data["startYear"].max())),
    )
    filtered_data_s = data[
        (data["startYear"] >= year_filter[0]) & (data["startYear"] <= year_filter[1]) & (data["runtimeMinutes"] != "")
    ]
    filtered_data_s["runtimeMinutes"] = filtered_data_s["runtimeMinutes"].astype(int)
    mean_runtime = filtered_data_s.groupby(["startYear", "titleType"])[["runtimeMinutes"]].mean().reset_index()
    fig = px.line(
        mean_runtime,
        x="startYear",
        y="runtimeMinutes",
        color="titleType",
        title="Film run time by title type",
        labels={"startYear": "Start year", "titleType": "Title type", "runtimeMinutes": "Run time (minutes)"},
        hover_data={"startYear": True, "titleType": True, "runtimeMinutes": True},
        color_discrete_sequence=px.colors.qualitative.Prism,
    )
    fig.update_layout(showlegend=True, height=600)
    st.plotly_chart(fig)

    filtered_data = data[(data["startYear"] >= year_filter[0]) & (data["startYear"] <= year_filter[1])]
    adult_data = st.selectbox("Select Adult", filtered_data["isAdult"].unique())
    mean_duration = filtered_data.groupby(["startYear", "isAdult", "titleType"])[["duration"]].mean().reset_index()
    mean_duration_df = mean_duration[mean_duration["isAdult"] == adult_data]
    fig = px.area(
        mean_duration_df,
        x="startYear",
        y="duration",
        color="titleType",
        line_group="titleType",
        title="Film duration by title type",
        labels={"startYear": "Start year", "titleType": "Title type", "duration": "Duration (years)"},
    )
    fig.update_layout(showlegend=True, height=600)
    st.plotly_chart(fig)


# %%


def pie_chart_genre():
    st.subheader("IMDB genres by year range (Choose Range)")
    year_filter = st.slider(
        "Year Range",
        (data["startYear"].min()),
        (data["startYear"].max()),
        ((data["startYear"].min()), int(data["startYear"].max())),
    )
    filtered_data = data[(data["startYear"] >= year_filter[0]) & (data["startYear"] <= year_filter[1])]
    genre = st.selectbox("Select Genre", genre_lst)

    fig = px.pie(filtered_data, names=genre, title=f"Genre counts for {genre}")
    fig.update_layout(showlegend=True, height=600)
    st.plotly_chart(fig)

    genre_time = data.groupby(["startYear", genre]).size().to_frame("Count").reset_index()
    time_count = data.groupby(["startYear"]).size().to_frame("Tot_count").reset_index()
    all_genre_time = pd.merge(time_count, genre_time, on="startYear", how="left")
    all_genre_time = all_genre_time.sort_values(["startYear", genre])
    all_genre_time["Perc"] = (all_genre_time["Count"] / all_genre_time["Tot_count"]) * 100
    fig = px.area(
        all_genre_time,
        x="startYear",
        y="Perc",
        color=genre,
        line_group=genre,
        title="Percentage films by genre",
        labels={"startYear": "Start year", "Perc": "Percentage"},
    )
    fig.update_layout(showlegend=True, height=600)
    st.plotly_chart(fig)


# %%
def main():
    st.sidebar.title("IMDB film names")
    page = st.sidebar.radio("Go to", ["Overview", "Title type counts", "Title type statistics", "Pie chart genres"])

    if page == "Overview":
        overview()
    elif page == "Title type counts":
        title_type_counts()
    elif page == "Title type statistics":
        title_type_stats()
    elif page == "Pie chart genres":
        pie_chart_genre()


if __name__ == "__main__":
    main()

# %%

# %%
