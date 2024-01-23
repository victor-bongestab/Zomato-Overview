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




# COUNTRIES ----------------------------------------

def countries_reg_cities_df():
    # Countries with most unique cities
    df_cities_by_country = ( df.loc[ : , ["country", "city"] ].groupby( ["country"] ).nunique()
                                                              .sort_values("city", ascending=False)
                                                              .reset_index() )
    
    reg_cities = df_cities_by_country.loc[ :4 , ["country", "city"] ]
    
    
    return adjust_df(reg_cities)



def countries_cuisines_df():
    # Countries with most unique cuisines
    df_cuisines_by_country = ( df.loc[ : , ["country", "cuisines"] ].groupby( ["country"] ).nunique()
                                                                    .sort_values("cuisines", ascending=False)
                                                                    .reset_index() )

    df_cuisines_by_country = df_cuisines_by_country.loc[ 0:4 , ["country", "cuisines"] ]

    return adjust_df(df_cuisines_by_country)



def countries_ratings_per_restaurant_df():
    # Most ratings per restaurant

    # Group votes by country and count votes
    df_num_votes_by_country = ( df.loc[ : , ["country", "votes"] ].groupby( ["country"] ).sum()
                                                                  .sort_values("votes", ascending=False)
                                                                  .reset_index() )


    # Group restaurants by country and count unique restaurants
    df_num_of_restaurants_by_country = ( df.loc[ : , ["country", "restaurant_id"] ].groupby( ["country"] ).nunique()
                                                                                   .sort_values("restaurant_id", ascending=False)
                                                                                   .reset_index() )

    # Merge df_num_votes_by_country and df_num_of_restaurants_by_country 
    # Create a new column with ratings_per_restaurant
    df_rate_ratings_by_country = pd.merge(df_num_votes_by_country, df_num_of_restaurants_by_country, how="inner")
    df_rate_ratings_by_country["ratings_per_restaurant"] = df_rate_ratings_by_country["votes"] / df_rate_ratings_by_country["restaurant_id"]
    df_rate_ratings_by_country["ratings_per_restaurant"] = df_rate_ratings_by_country["ratings_per_restaurant"]

    # Use only country and ratings_per_restaurant
    top_ratings_per_restaurant = df_rate_ratings_by_country.sort_values("ratings_per_restaurant", ascending=False).reset_index(drop=True)
    
    top_ratings_per_restaurant = top_ratings_per_restaurant.loc[ :4, ["country", "ratings_per_restaurant" ] ]
    top_ratings_per_restaurant['ratings_per_restaurant'] = top_ratings_per_restaurant['ratings_per_restaurant'].astype(int)

    
    return adjust_df(top_ratings_per_restaurant)



def countries_delivery_presence_df():
    #SA Name of country with best frequency of delivery option.

    # Create a df_num_deliverers with only delivering restaurants.
    df_num_deliverers = df.loc[ (df.loc[ : , "is_delivering_now" ] == 1) , : ]

    # Group restaurants by country and count unique restaurants delivering
    df_num_of_restaurants_by_country = ( df.loc[ : , ["country", "restaurant_id"] ].groupby( ["country"] ).nunique()
                                                                                   .sort_values("restaurant_id", ascending=False)
                                                                                   .reset_index() )
    
    df_num_of_restaurants_by_country.rename(columns = {'restaurant_id':'total_restaurants'}, inplace = True)

    # Group restaurants by country and count them all
    df_num_deliv_by_country = ( df_num_deliverers.loc[ : , ["country", "restaurant_id"] ].groupby( ["country"] ).count()
                                                                                         .sort_values("restaurant_id", ascending=False)
                                                                                         .reset_index() )
    df_num_deliv_by_country.rename(columns = {'restaurant_id':'delivery_options'}, inplace = True)

    # Merge df_num_deliv_by_country and df_num_of_restaurants_by_country. 
    # Create a new column with delivery_presence =  delivery_options / total_restaurants
    df_freq_deliv_by_country = pd.merge(df_num_deliv_by_country, df_num_of_restaurants_by_country, on="country", how="inner")
    df_freq_deliv_by_country["delivery_presence"] = (df_freq_deliv_by_country["delivery_options"] / df_freq_deliv_by_country["total_restaurants"])
    df_freq_deliv_by_country['delivery_presence'] = df_freq_deliv_by_country['delivery_presence'].apply(lambda x: f'{x:.2%}')

    df_freq_deliv_by_country = df_freq_deliv_by_country[['country', 'total_restaurants', 'delivery_options', 'delivery_presence']]

    
    return adjust_df(df_freq_deliv_by_country)



def country_ratings_avg_chart():
    # Best and Worst rated countries
    
    # Group by Ratings
    df_ratings = ( df.loc[ : , ["country", "aggregate_rating"] ].groupby( ["country"] ).mean()
                                                                .sort_values("aggregate_rating", ascending=False)
                                                                .reset_index() )

    top3_bottom3 = pd.concat( [df_ratings.head(3), df_ratings.tail(3)] )
    mean_rating = df_ratings['aggregate_rating'].mean()
    
    # Setting ratings colors
    top3_bottom3['color'] = ['skyblue' if country in top3_bottom3.head(3)['country'].values else 'indianred' for country in top3_bottom3['country']]
    
    # Defining chart data
    fig = go.Figure(data=[go.Bar( x=top3_bottom3['country'],
                                  y=top3_bottom3['aggregate_rating'],
                                  text=top3_bottom3['aggregate_rating'],
                                  marker_color=top3_bottom3['color'], opacity=0.9 )])

    fig.add_shape(type='line', x0=-0.5, x1=len(top3_bottom3)-0.5, y0=mean_rating, y1=mean_rating,
                  line=dict(color='gray', width=1, dash='dash'))

    fig.update_layout(title_text='Top 3 and Bottom 3 countries on Avg Rating (gray line is overall avg)',
                      xaxis_title='Country', yaxis_title='Average Rating', bargap=0.1, title_font=dict(size=18.5),
                      xaxis=dict(tickangle=45, tickmode='array'))

    fig.update_traces(textposition='inside', texttemplate='%{text:.2f}', textfont=dict(size=12), hoverinfo='text+y', insidetextanchor='start')

    return fig



def countries_avg_cost_chart():
    # Bar plot of average cost for two in dollars in each country
    df_cost_by_country = ( df.loc[ : , ["country", "dollar_average_cost_for_two"] ].groupby( ["country"] ).mean()
                                                                                   .sort_values("dollar_average_cost_for_two", ascending=False)
                                                                                   .reset_index() )

    # Plot
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_cost_by_country['country'],
        y=df_cost_by_country['dollar_average_cost_for_two'],
        marker_color='skyblue' ))

    fig.update_layout(
        title='Average Cost for Two by Country',
        xaxis_title='Country',
        yaxis_title='Average Cost for Two (in dollars)',
        width=1100, title_font=dict(size=24), title_x=0.05,
        xaxis=dict(tickangle=45, tickmode='array'))

    return fig




# CITIES ----------------------------------------

def cities_most_excellent_restaurants_chart():
    #SA Barplot of cities with most 4.5+ rating restaurants.
    df_good_ratings = df.loc[ df["aggregate_rating"] >= 4.5, :]

    df_restaurants_by_city_and_good_rating = ( df_good_ratings.loc[ : , ["city", "restaurant_id"] ].groupby( ["city"] ).nunique()
                                                                                                   .sort_values("restaurant_id", ascending=False)
                                                                                                   .reset_index() )

    df_restaurants_by_city_and_good_rating.columns = ["city", "number_of_well_rated_restaurants"]
    top_10_cities = df_restaurants_by_city_and_good_rating.loc[ :9, : ]
    top_10_cities = pd.merge(top_10_cities, df[['city', 'country']], on='city', how='inner').drop_duplicates().reset_index(drop=True)

    
    # Bar chart
    fig = go.Figure(data=[go.Bar( x=top_10_cities['city'],
                                  y=top_10_cities['number_of_well_rated_restaurants'],
                                  hovertemplate=top_10_cities['country'],
                                  marker_color='skyblue' )])

    fig.update_layout(title_text='Cities with most restaurants rated as Excellent',
                      xaxis_title='City', yaxis_title='Amount of Excellent Restaurants',
                      width=1100, title_font=dict(size=24), title_x=0.05)
    

    return fig



def cities_restaurant_pop_chart():
    # Barplot of amount of cities with certain restaurant populations
    df_restaurants_by_city = ( df.loc[ : , ["city", "restaurant_id"] ].groupby( ["city"] ).nunique()
                                                                      .sort_values("restaurant_id", ascending=False)
                                                                      .reset_index() )

    df_restaurants_by_city.columns = ["city", "number_of_restaurants"]


    cat = ['1-20', '21-40', '41-60', '61+']

    df_restaurants_by_city['number_of_restaurants'] = df_restaurants_by_city['number_of_restaurants'].apply( lambda x: cat[0] if x<=20 else 
                                                                                                                       cat[1] if ( (x>20) & (x<=40) ) else
                                                                                                                       cat[2] if ( (x>40) & (x<=60) ) else
                                                                                                                       cat[3] )

    df_restaurants_by_city = df_restaurants_by_city.loc[ :, [ 'number_of_restaurants', 'city' ] ].groupby('number_of_restaurants').count().reset_index()


    # Barplot
    fig = go.Figure()

    fig.add_trace(go.Bar(
                    x=df_restaurants_by_city['number_of_restaurants'],
                    y=df_restaurants_by_city['city'],
                    marker_color='indianred'))

    fig.update_layout(
        title='How many cities have restaurant population of 1-20, 21-40, 41-60 and 61+?',
        xaxis_title='Restaurant population rate',
        yaxis_title='Amount of Cities', width=500, title_font=dict(size=16),
        xaxis=dict(tickangle=45, tickmode='array'))

    return fig



def cities_delicery_chart():
    #SA Pie chart delivery presence
    cities_delivery_option = ( df.loc[ : , ["city", "is_delivering_now"] ].groupby( ["city"] ).sum().reset_index() )

    
    # Labels and Values for Pie Chart
    cities_deliver_label = [ 'Yes', 'No' ]
    cities_deliver_values = [ cities_delivery_option[cities_delivery_option['is_delivering_now'] != 0].shape[0], 
                              cities_delivery_option[cities_delivery_option['is_delivering_now'] == 0].shape[0] ]

    # Pie chart
    fig = go.Figure(data=[go.Pie( labels=cities_deliver_label, 
                                  values=cities_deliver_values, 
                                  marker=dict(colors=['dodgerblue', 'indianred']) )])

    fig.update_layout( title_text='% of cities that have Delivery option', title_x=0.25 )

    return fig



def cities_cost_df():
    #SA Table with most expensive cities for two people dishes.
    
    # Most expensive cities
    df_city_by_cost_for_two = ( df.loc[ : , ["city", "dollar_average_cost_for_two", "country"] ].groupby( ["city"] ).mean("dollar_average_cost_for_two")
                                                                                                         .sort_values("dollar_average_cost_for_two", ascending=False)
                                                                                                         .reset_index() )

    top_cities_df = df_city_by_cost_for_two.head(5)
    
    # Add cities' countries
    top_cities_df = pd.merge(top_cities_df, df[['city', 'country']], on='city', how='inner').drop_duplicates().reset_index(drop=True)


    # Add countries' cost rankings
    df_cost_by_country = ( df.loc[ : , ["country", "dollar_average_cost_for_two"] ].groupby( ["country"] ).mean()
                                                                                   .sort_values("dollar_average_cost_for_two", ascending=False)
                                                                                   .reset_index() )

    df_cost_by_country['country_cost_rank'] = df_cost_by_country['dollar_average_cost_for_two'].rank(ascending=False).astype(int)
    df_cost_by_country.drop( ['dollar_average_cost_for_two'], axis=1, inplace=True )

    cities_cost_rank_df = pd.merge(top_cities_df, df_cost_by_country, on='country', how='inner').drop_duplicates()
    
    return adjust_df(cities_cost_rank_df)


    
def cities_diversity_cuisine_chart():
    #SA Table with cities with most variety of cuisines.
    cities_cuisines_df = ( df.loc[ : , ["city", "cuisines"] ].groupby( ["city"] ).nunique()
                                                             .sort_values("cuisines", ascending=False)
                                                             .reset_index() )

    cities_cuisines_df['diversity'] = cities_cuisines_df['cuisines'].apply( lambda x: 'low' if x<10 else 'high' )


    # Labels and Values for Pie Chart
    diversity = [ 'High', 'Low' ]

    diversity_counts = []
    diversity_counts.append( cities_cuisines_df[ cities_cuisines_df['diversity'] == 'high' ].shape[0] )
    diversity_counts.append( cities_cuisines_df[ cities_cuisines_df['diversity'] == 'low' ].shape[0] )

    # Pie chart
    fig = go.Figure(data=[go.Pie( labels=diversity, 
                                  values=diversity_counts, 
                                  marker=dict(colors=['dodgerblue', 'indianred']) )])

    fig.update_layout( title_text='Most Cities have high or low diversity of Cuisines?', title_x=0.25 )

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


st.sidebar.markdown("""---""") #linha divisória



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
st.markdown('# Geographic Overview')


tab1, tab2 = st.tabs(['Countries', 'Cities'])

with tab1:
    # Container 01
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Countries with most Cities registered")
            st.dataframe( countries_reg_cities_df() )
            
        with col2:
            st.markdown('### Countries with most unique Cuisines')
            st.dataframe( countries_cuisines_df() )

    
    # Container 02
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('### Best Rating frequence')
            st.dataframe( countries_ratings_per_restaurant_df() )
            
            st.markdown('### Delivery frequence')
            st.dataframe( countries_delivery_presence_df() )
            
        with col2:
            country_ratings_avg_chart = country_ratings_avg_chart()
            country_ratings_avg_chart.update_layout(width=550, height=600)
            st.plotly_chart( country_ratings_avg_chart )
    
    
    # Container 03
    with st.container():
        st.plotly_chart( countries_avg_cost_chart(), use_container_width=True )

        
        
        
        
with tab2:
    # Container 01
    with st.container():
        st.plotly_chart( cities_most_excellent_restaurants_chart() )

    
    # Container 02
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart( cities_restaurant_pop_chart(), use_container_width=True )
            
        with col2:
            st.plotly_chart( cities_delicery_chart(), use_container_width=True )
    
    
    # Container 03
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('### Most Expensive Cities')
            st.dataframe( cities_cost_df() )
            
        with col2:
            st.plotly_chart( cities_diversity_cuisine_chart(), use_container_width=True )
        