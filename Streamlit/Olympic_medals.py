import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

path_folder = Path("/Users/keithlowton/Desktop/Ks/Python code/Kaggle/Country Medals")
print(path_folder.exists())
print(path_folder)


# Load dataset
data = pd.read_csv(os.path.join(path_folder, "data/Summer_olympic_Medals.csv"))
print(data.shape)
# (1344, 8)


# Helper function to get medal counts
def get_medal_counts(df, group_by_column):
    return df.groupby([group_by_column])[["Gold", "Silver", "Bronze"]].sum().reset_index()


def page_overview():
    st.subheader("Global Medal Counts By Year Range (Choose Range)")
    year_filter = st.slider(
        "Year Range",
        int(data["Year"].min()),
        int(data["Year"].max()),
        (int(data["Year"].min()), int(data["Year"].max())),
    )
    filtered_data = data[(data["Year"] >= year_filter[0]) & (data["Year"] <= year_filter[1])]
    medal_counts = get_medal_counts(filtered_data, "Country_Name")
    medal_counts["Total"] = medal_counts["Gold"] + medal_counts["Silver"] + medal_counts["Bronze"]
    top_countries = medal_counts.sort_values(by="Total", ascending=False).head(20)
    # st.subheader("Top 20 Countries by Total Medals")
    fig = px.bar(
        top_countries,
        x="Total",
        y="Country_Name",
        orientation="h",
        title="Top 20 Countries by Total Medals",
        color="Country_Name",
        hover_data={"Total": True, "Gold": True, "Silver": True, "Bronze": True},
        color_discrete_sequence=px.colors.qualitative.Prism,
    )
    fig.update_layout(showlegend=False, height=600)
    st.plotly_chart(fig)


def page_country_analysis():
    st.subheader("Country-Specific Analysis")

    country = st.selectbox("Select Country", data["Country_Name"].unique())
    country_data = data[data["Country_Name"] == country]
    # st.subheader(f"Medal Count for {country}")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=country_data["Year"], y=country_data["Gold"], mode="lines", name="Gold", line=dict(color="gold", width=2)
        )
    )
    fig.add_trace(
        go.Scatter(
            x=country_data["Year"],
            y=country_data["Silver"],
            mode="lines",
            name="Silver",
            line=dict(color="silver", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=country_data["Year"],
            y=country_data["Bronze"],
            mode="lines",
            name="Bronze",
            line=dict(color="#cd7f32", width=2),
        )
    )
    fig.update_layout(title=f"Medal Count for {country} Over the Years", height=400)
    st.plotly_chart(fig)
    total_medals = country_data[["Gold", "Silver", "Bronze"]].sum().reset_index()
    total_medals.columns = ["Medal Type", "Count"]
    # st.subheader(f"Total Medals for {country}")
    fig = px.bar(
        total_medals,
        x="Count",
        y="Medal Type",
        orientation="h",
        title=f"Total Medals for {country}",
        color="Medal Type",
        color_discrete_map={"Gold": "gold", "Silver": "silver", "Bronze": "#cd7f32"},
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig)


def page_choropleth():
    # st.subheader("Choropleth Mapping")

    year = st.selectbox("Select Year", sorted(data["Year"].unique()), key="year_select")
    year_data = data[data["Year"] == year]
    medal_counts = get_medal_counts(year_data, "Country_Name")
    medal_counts["Total"] = medal_counts["Gold"] + medal_counts["Silver"] + medal_counts["Bronze"]
    st.subheader(f"Global Distribution of Total Medals in {year}")
    fig = px.choropleth(
        medal_counts,
        locations="Country_Name",
        locationmode="country names",
        color="Total",
        hover_name="Country_Name",
        hover_data={"Total": True, "Gold": True, "Silver": True, "Bronze": True},
        color_continuous_scale=px.colors.sequential.YlOrBr,
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig)
    st.subheader(f"Medal Counts by Country in {year}")
    sorted_medal_counts = medal_counts.sort_values(by="Total", ascending=False)
    st.dataframe(sorted_medal_counts, hide_index=True)


def main():
    st.sidebar.title("Summer Olympic Medals")
    page = st.sidebar.radio("Go to", ["Global Medals", "Country Analysis", "Global Mapping"])

    if page == "Global Medals":
        page_overview()
    elif page == "Country Analysis":
        page_country_analysis()
    elif page == "Global Mapping":
        page_choropleth()


if __name__ == "__main__":
    main()
