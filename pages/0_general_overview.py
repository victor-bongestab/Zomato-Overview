# IMPORTS
import pandas as pd
import inflection

import streamlit as st
from PIL import Image

from streamlit_folium import folium_static, st_folium
import folium
from folium.plugins import MarkerCluster


# Dataset
df_raw = pd.read_csv('zomato.csv')
df = df_raw.copy()



# CODE FUNCTIONS
# ==============================================================================================================================================

# DATA CLEANING
# ==============================================================================================================================================

def clean_code(df):
    # Dropping duplicates.
    df.drop_duplicates(inplace=True)


    # Deleting rows with NaN values
    for col in df:
        df = df.loc[ (df[col].isnull() == False) , :]


    # Making new columns to better describe the informations we have.
    #

    # Rename the columns to something_like_this.
    def rename_columns(dataframe):
        df = dataframe.copy()

        title = lambda x: inflection.titleize(x)
        snakecase = lambda x: inflection.underscore(x)
        spaces = lambda x: x.replace(" ", "")

        cols_old = list(df.columns)
        cols_old = list(map(title, cols_old))
        cols_old = list(map(spaces, cols_old))
        cols_new = list(map(snakecase, cols_old))

        df.columns = cols_new
        return df

    df = rename_columns(df).copy()



    # Defining countries codes by their names.
    countries = {
                1: "India",
                14: "Australia",
                30: "Brazil",
                37: "Canada",
                94: "Indonesia",
                148: "New Zeland",
                162: "Philippines",
                166: "Qatar",
                184: "Singapure",
                189: "South Africa",
                191: "Sri Lanka",
                208: "Turkey",
                214: "United Arab Emirates",
                215: "England",
                216: "United States of America",
                }

    def country_name(country_id):
        return countries[country_id]

    df["country"] = df["country_code"].apply(country_name)



    # Defining price ranges with a more intuitive description.
    def create_price_type(price_range):
        if price_range == 1:
            return "cheap"
        elif price_range == 2:
            return "normal"
        elif price_range == 3:
            return "expensive"
        else:
            return "gourmet"

    df["price_type"] = df["price_range"].apply(create_price_type)



    # Transforming the hex code to color name.
    colors = {
            "3F7E00": "darkgreen",
            "5BA829": "green",
            "9ACD32": "lightgreen",
            "CDD614": "lemon",
            "FFBA00": "yellow",
            "CBCBC8": "gray",
            "FF7800": "orange",
            }

    def color_name(hex_code):
        return colors[hex_code]

    df["rating_color"] = df["rating_color"].apply(color_name)



    # Translating the rating text.
    rating_text = {
                    "darkgreen": "Excellent",
                    "green": "Very Good",
                    "lightgreen": "Good",
                    "lemon": "Average",
                    "yellow": "Average",
                    "gray": "Not rated",
                    "orange": "Poor",
                    }

    def rating_translation(rating_color):
        return rating_text[rating_color]

    df["rating_text"] = df["rating_color"].apply(rating_translation)



    # Also use only one type of cuisine for the restaurants.
    df["cuisines"] = df.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])



    # Convert every currency to Dollar and delete absurd values (over $ 10.000 a meal)
    currency_convertion_to_dollar = {
                                    'Botswana Pula(P)': 0.076,
                                    'Brazilian Real(R$)': 0.21,
                                    'Dollar($)': 1.0,
                                    'Emirati Diram(AED)': 0.27,
                                    'Indian Rupees(Rs.)': 0.012,
                                    'Indonesian Rupiah(IDR)': 0.000067,
                                    'NewZealand($)': 0.64,
                                    'Pounds(£)': 1.31,
                                    'Qatari Rial(QR)': 0.27,
                                    'Rand(R)': 0.055,
                                    'Sri Lankan Rupee(LKR)': 0.0031,
                                    'Turkish Lira(TL)': 0.038
                                    }

    def price_in_dollar(original_currency, original_price):
        return currency_convertion_to_dollar[original_currency] * original_price

    df["dollar_average_cost_for_two"] = df.apply(lambda x: price_in_dollar(x["currency"], x["average_cost_for_two"]), axis=1)
    df = df.loc[ (df["dollar_average_cost_for_two"] < 1000) ,:]


    # Reset index after cleaning everything.
    return df.reset_index(drop=True)

df = clean_code(df)

# ==============================================================================================================================================
# STREAMLIT
# ==============================================================================================================================================


# PAGE LAYOUT
st.set_page_config(page_title= 'Zomato',page_icon= '🟥',layout= 'wide' )



# BARRA LATERAL
# ============================================

# Imagem da barra lateral
image_path = 'img/'
image_sidebar = Image.open(image_path + "zomato_logo.png")
st.sidebar.image(image_sidebar, width=160)


st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)


st.sidebar.markdown("""---""")



# Primeira seção da barra lateral
st.sidebar.markdown('# Welcome! ')
st.sidebar.markdown("Let's take a tour around the company.")
st.sidebar.markdown("""---""")


# Segunda seção da barra lateral
# My LinkedIn URL
linkedin_url = "https://www.linkedin.com/in/victor-bongestab/"
name = "Victor Bongestab"

st.sidebar.markdown(f"[![LinkedIn](https://img.icons8.com/color/48/000000/linkedin.png)]({linkedin_url}) {name}")




# LAYOUT da tela principal
# ============================================

# TÍTULO principal
top_image = Image.open(image_path + "zomato.png")
st.image(top_image)



with st.container():
    # Container 01
    st.markdown("## General Overview")
    
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        num_of_unique_countries = len( df["country"].unique() )
        st.metric(label='Countries', value=num_of_unique_countries)

        
    with col2:
        num_of_unique_cities = len( df["city"].unique() )
        st.metric(label='Cities', value=num_of_unique_cities)


    with col3:
        num_of_unique_restaurants = len( df["restaurant_id"].unique() )
        st.metric(label='Restaurants', value=num_of_unique_restaurants)
        
    
    with col4:
        num_of_unique_cuisines = len( df["cuisines"].unique() )
        st.metric(label='Cuisines', value=num_of_unique_cuisines)
        
    
    with col5:
        num_of_unique_ratings = df["votes"].sum()
        st.metric(label='Total Votings', value="{:,}".format(num_of_unique_ratings))
        
    
    with col6:
        average_rating = df["aggregate_rating"].mean().round(2)
        st.metric(label='Avg Rating', value=average_rating)
        
        
        
with st.container():
    # Container 02
    st.markdown("## World Map")
    
    # Plot map
    center_latitude = df['latitude'].mean()
    center_longitude = df['longitude'].mean()

    locations = df[['latitude','longitude']].values.tolist()
    popups = df[['city','restaurant_name','aggregate_rating']].values.tolist()


    mapa = folium.Map(location=[center_latitude, center_longitude], zoom_start=2.4)

    MarkerCluster(locations=locations, popups=popups).add_to(mapa)

    st_data = st_folium(mapa, use_container_width=True)
    #folium_static(mapa, width=1000, height=600)