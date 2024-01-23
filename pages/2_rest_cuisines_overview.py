# IMPORTS
import pandas as pd
import inflection

import streamlit as st
from PIL import Image

import plotly.express as px
import plotly.graph_objects as go


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
# HELPER FUNCTIONS

def adjust_df(df):
    # Index starting from 1
    df.index = df.index + 1
    
    return df




def votes_restaurants_voting_chart():
    # Pie chart votes for online and offline restaurants
    votes_count_online_or_not = df.loc[:, ["has_online_delivery", "votes"]].groupby(["has_online_delivery"]).mean().reset_index()

    
    # Pie chart
    fig = go.Figure(data=[go.Pie( labels=[ 'Restaurants Offline', 'Restaurants Online' ], 
                                  values=votes_count_online_or_not['votes'], 
                                  marker=dict(colors=['dodgerblue', 'indianred']) )])

    fig.update_layout( title_text='Votes amount', title_x=0.25, title_font=dict(size=24) )
    
    return fig



def restaurants_booking_ratings_df():
    # Ratings with and without reservation.
    ratings_table_booking_df = df.loc[:, ["has_table_booking", "aggregate_rating"]].groupby(["has_table_booking"]).mean().reset_index().round(2)
    ratings_table_booking_df['aggregate_rating'] = ratings_table_booking_df['aggregate_rating'].astype(str)
    
    return adjust_df(ratings_table_booking_df)



def cuisines_deliver_chart():
    #SA Barplot of cuisines delivering online
    df_online_cuisine = df.loc[ df["has_online_delivery"] == 1, :]

    cuisines_restaurants_online = ( df_online_cuisine.loc[ : , ["cuisines", "restaurant_id"] ].groupby( ["cuisines"] ).nunique()
                                                                                                 .sort_values("restaurant_id", ascending=False)
                                                                                                 .reset_index() )

    cuisines_restaurants_online.columns = ["cuisines", "restaurants_with_delivery_option"]
    cuisines_restaurants_online = cuisines_restaurants_online.loc[ 0:4 , : ]


    # Bar chart
    fig = go.Figure(data=[go.Bar( x=cuisines_restaurants_online['cuisines'],
                                  y=cuisines_restaurants_online['restaurants_with_delivery_option'],
                                  marker_color='skyblue' )])

    fig.update_layout(title_text='Cuisines x Amount of Restaurants delivering online',
                      xaxis_title='Cuisine', yaxis_title='Restaurants')


    return fig



def cuisines_cost_chart():
    #SA Barplot Cuisines cost.
    cuisines_cost = ( df.loc[ : , ["cuisines", "dollar_average_cost_for_two"] ].groupby( ["cuisines"] ).mean()
                                                                               .sort_values("dollar_average_cost_for_two", ascending=False)
                                                                               .reset_index() )

    cuisines_cost['dollar_average_cost_for_two'] = cuisines_cost['dollar_average_cost_for_two'].astype(int)
    cuisines_cost = cuisines_cost.loc[ 0:4 , : ]


    fig = go.Figure(data=[go.Bar( x=cuisines_cost['cuisines'],
                                  y=cuisines_cost['dollar_average_cost_for_two'],
                                  marker_color='indianred' )])

    fig.update_layout(title_text='Most expensive Cuisines for two people (dollars)',
                      xaxis_title='Cuisine', yaxis_title='Cost for two')


    return fig



def cuisines_favorites_chart():
    # Sunburst of countries' favorite dishes
    df_cuisines_by_country = ( df.loc[ : , ['cuisines', 'aggregate_rating', 'country'] ].groupby( ["country", "cuisines"] ).mean()
                                                                                        .reset_index() ).round(2) 

    cuisines_countries_favorites_df = ( df_cuisines_by_country.loc[ : , ["cuisines", "aggregate_rating", "country"] ].groupby( ["country"] ).max()
                                                                                                                  .reset_index() )

    cuisines_countries_favorites_df.sort_values('cuisines')


    # Sunburst chart
    fig = px.sunburst(cuisines_countries_favorites_df, path=['cuisines', 'country'], color='country', color_discrete_sequence=px.colors.qualitative.Set3)

    fig.update_layout(title_text="Countries' favorite Cuisines", title_x=0.4)

    return fig




# ==============================================================================================================================================
# STREAMLIT
# ==============================================================================================================================================


# PAGE LAYOUT
st.set_page_config(page_title= 'Zomato', page_icon= '🟥', layout= 'wide' )



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
st.markdown('# Restaurants and Cuisines Overview')
st.markdown("""---""")


with st.container():
    # Container 01
    col1, col2 = st.columns(2)
        
    with col1:
        st.plotly_chart( votes_restaurants_voting_chart(), use_container_width=True )
            
    with col2:
        st.markdown('### Restaurant Ratings')
        st.dataframe( restaurants_booking_ratings_df(), use_container_width=True )
        
    
    
    
with st.container():
    # Container 02
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart( cuisines_deliver_chart(), use_container_width=True )
            
    with col2:
        st.plotly_chart( cuisines_cost_chart(), use_container_width=True )
    
    
    
with st.container():
    # Container 03
    st.plotly_chart( cuisines_favorites_chart(), use_container_width=True )