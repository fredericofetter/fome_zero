# Libraries
import pandas as pd
import streamlit as st

import plotly.express as px
import inflection

from PIL import Image

import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster


from utils import *




'''

##########################################################################################
# DEFINIÇÃO DE FUNÇÕES
##########################################################################################

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')



def country_name(country_id):
    COUNTRIES = {
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
    return COUNTRIES[country_id]




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




def color_name(color_code):
    COLORS = {
            "3F7E00": "darkgreen",
            "5BA829": "green",
            "9ACD32": "lightgreen",
            "CDD614": "orange",
            "FFBA00": "red",
            "CBCBC8": "darkred",
            "FF7800": "darkred",
            }
    return COLORS[color_code]




def clean_data(df1, cutoff=5000000):
'''
#    Esta tem a responsabilidade de fazer a limpeza dos dados:
#    
#    Tipos de limpeza:
#    1. Remover colunas sem variabilidade
#    2. Converter a coluna 'Restaurant ID' para int para facilitar ordenamento
#    3. Remover entradas faltantes
#    4. Remover linhas duplicadas
#    5. Remover outliers no 'Average Cost for two'
#    6. Escolher ficar apenas com a primeira culinária de cada restaurante. 
#    7. Renomear as colunas removento espaços e letras maiúsculas.

'''
    df1 = df1.drop(['Switch to order menu'], axis=1)

    # converter ID para str
    df1['Restaurant ID'] = df1['Restaurant ID'].astype(str)

    # Remover valores faltantes da coluna Cuisines
    df1 = df1[df1['Cuisines'].notnull()]
    df1 = df1[df1['Rating text'] != 'Not rated']
    df1 = df1[df1['Average Cost for two'] > 0]

    #remover linhas duplicadas
    df1 = df1.drop_duplicates()

    #Remover Outliers
    df1 = df1[df1['Average Cost for two'] < cutoff]

    # escolher apenas uma culinária
    df1["Cuisines"] = df1.loc[:, "Cuisines"].apply(lambda x: x.split(",")[0])

    # renomeia as colunas
    df1 = rename_columns(df1)
    
    df1['rating_color'] = df1['rating_color'].apply(color_name)
    
    return df1

def get_countries(df1):
    countries = df1['country_code'].apply(country_name).unique()
    countries.sort()
    return countries

def get_cities(df1):
    cities = df1['city'].unique()
    cities.sort()
    return cities

def get_cuisines(df1):
    cuisines = df1['cuisines'].unique()
    cuisines.sort()
    return cuisines

def get_no_votes(df1):
    no_votes = df1['votes'].sum()
    return no_votes

def get_no_rest_cadastrados(df1):
    no_rest = df1.shape[0]
    return no_rest

def get_no_paises_cadastrados(df1):
    no_countries = len(get_countries(df1))
    return no_countries

def get_no_cidades_cadastradas(df1):
    no_cities = len(get_cities(df1))
    return no_cities

def get_no_cuisines(df1):
    no_cuisines = len(get_cuisines(df1))
    return no_cuisines



def plot_map(df1): 

    m = folium.Map(location=[25, 10], zoom_start=1.75)

    marker_cluster = MarkerCluster().add_to(m)
    
    for index, row in df1.iterrows():
        folium.Marker([row['latitude'], row['longitude']],
                      popup=row[['restaurant_name','city', 'average_cost_for_two', 'aggregate_rating', 'cuisines']], 
                      icon=folium.Icon(color=row['rating_color'], icon="ok-sign")
                     ).add_to( marker_cluster )
    

    folium_static( m, width=1024, height=600)
    return


def get_best_restaurant(df1, cuisine):
    df_aux = df1[df1['cuisines'] == cuisine]
    max_rating = df_aux['aggregate_rating'].max()
    df_aux = df_aux[df_aux['aggregate_rating'] == max_rating]
    max_rating_id = df_aux['restaurant_id'].astype(int).min()
    max_rating_name = df_aux.loc[df_aux['restaurant_id'].astype(int) == max_rating_id, 'restaurant_name'].values[0]
    
    return max_rating_name, max_rating



def plot_countries_bars(df1, y_ax):
    
    axis_labels = {'restaurant_id':'Quantidade de Restaurantes', 
                   'country':'Países', 
                   'city':'Quantidade de Cidades', 
                   'votes':'Número Médio de Avaliações por Restaurante', 
                   'average_cost_for_two':'Custo Médio para Duas Pessoas'
                  }
    
    title_filler = {'restaurant_id':'Quantidade de Restaurantes', 
                   'country':'Países', 
                   'city':'Quantidade de Cidades', 
                   'votes':'Número Médio de Avaliações por Restaurante', 
                   'average_cost_for_two':'Custo Médio para Duas Pessoas'
                   }
    
    function_used = {'restaurant_id':'count', 
                     'country':'count', 
                     'city':'count', 
                     'votes':'mean',
                     'average_cost_for_two':'mean'}
    
#    st.dataframe(df1[['country_code', y_ax]].head(10))
    
    df_aux = df1[['country_code', y_ax]]
#    st.dataframe(df_aux.head(10))
    if y_ax in ['city']:
        df_aux = df_aux.drop_duplicates()
    df_aux = df_aux.groupby(by=['country_code']).agg({y_ax : function_used[y_ax]}).reset_index().round(2)
#    st.dataframe(df_aux.head(10))
    df_aux['country'] = df_aux['country_code'].apply(country_name)
    df_aux = df_aux.sort_values(by=y_ax, ascending=False)
    
#    st.dataframe(df_aux.head(10))
    
    histogram_option_x = 'country'
    histogram_option_y = y_ax
    column_depicted = histogram_option_x
    y_axis = histogram_option_y

    fig = px.bar( df_aux, x=column_depicted, y=y_axis, 
                  text_auto=True, 
                  title='{} Registrados por País'.format(title_filler[y_axis]), 
                  labels=axis_labels)
    st.plotly_chart( fig, use_container_width=True )
    
    return
'''

##########################################################################################
# Loading Data
##########################################################################################


# Import dataset
df = pd.read_csv( 'dataset/zomato.csv' )

df1 = df.copy() #copied to preserve original dataframe




##########################################################################################
# LIMPEZA
##########################################################################################

df1 = clean_data(df1)

##########################################################################################
# BARRA LATERAL
##########################################################################################

image_path = 'images/logo_test.png'
image = Image.open( image_path )

logo_width = st.sidebar.slider(
    '### Qual a largura do logo', 
    value=120, 
    min_value=10, 
    max_value=250,
    #format='DD-MM-YYYY'
)

st.sidebar.image( image, width=logo_width )


#----------------------------------

st.sidebar.markdown( """---""" )

st.sidebar.markdown('### Filtros')

countries_selected = st.sidebar.multiselect(
    'Escolha os países que deseja visualizar as Informações', 
    get_countries(df1), default=['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia']
)


n_top_rest = st.sidebar.slider(
    '### Quantas cidades com mais restaurantes quer visualizar', 
    value=10, 
    min_value=1, 
    max_value=20,
    #format='DD-MM-YYYY'
)


agg_upper_cutoff = st.sidebar.slider(
    '### Qual a maior avaliação de restaurantes que deseja visualizar', 
    value=4., 
    min_value=1., 
    max_value=5.,
    step=0.05
    #format='DD-MM-YYYY'
)



agg_lower_cutoff = st.sidebar.slider(
    '### Qual a menor avaliação de restaurantes que deseja visualizar', 
    value=3., 
    min_value=1., 
    max_value=5.,
    step=0.05
    #format='DD-MM-YYYY'
)


n_top_cuisines = st.sidebar.slider(
    '### Quantas cidades com mais culinárias quer visualizar', 
    value=10, 
    min_value=1, 
    max_value=20,
    #format='DD-MM-YYYY'
)


##########################################################################################
# CAMPO PRINCIPAL
##########################################################################################


st.markdown('# 	:cityscape: Visão Cidades')

linhas_selecionadas = df1['country_code'].apply( country_name ).isin( countries_selected )
df1 = df1[linhas_selecionadas]




with st.container():
    
#    n_top = 10
    
#    df_aux = df1[['restaurant_id', 'country_code', 'city']].groupby(by=['country_code', 'city']).count().reset_index()
#    df_aux['country'] = df_aux['country_code'].apply( country_name )
#    df_aux = df_aux.sort_values(by='restaurant_id', ascending=False).reset_index(drop=True)
#    df_aux = df_aux.head(n_top)
    
#    histogram_option_x = 'city'
#    histogram_option_y = 'restaurant_id'
#    column_depicted = histogram_option_x
#    y_axis = histogram_option_y
#    fig = px.bar( df_aux, x=column_depicted, y=y_axis, color='country', title='Top {} cidades com mais restaurantes registrados'.format(n_top) )
#    fig.update_layout(xaxis={'categoryorder':'total descending'})
#    st.plotly_chart( fig, use_container_width=True )
    
    plot_cities_bars(df1, y_ax='restaurant_id', n_top=n_top_rest, agg_upper_cutoff=10, agg_lower_cutoff=-1)
    
    
with st.container():
    col1, col2 = st.columns( 2 )
    
   
    with col1.container():
        
#        n_top = 7
#        
#        df_aux = df1[df1['aggregate_rating'] > 4]
#        df_aux = df_aux[['aggregate_rating', 'country_code', 'city']].groupby(by=['country_code', 'city']).count().reset_index()
#        df_aux['country'] = df_aux['country_code'].apply(country_name)
#        df_aux = df_aux.sort_values(by='aggregate_rating', ascending=False).reset_index(drop=True)
#        df_aux = df_aux.head(n_top)

#        histogram_option_x = 'city'
#        histogram_option_y = 'aggregate_rating'
#        column_depicted = histogram_option_x
#        y_axis = histogram_option_y
#        fig = px.bar( df_aux, x=column_depicted, y=y_axis, color='country', title='Top {} cidades com em número de restaurantes com avaliação média acima de 4'.format(n_top))
#        fig.update_layout(xaxis={'categoryorder':'total descending'})
#        st.plotly_chart( fig, use_container_width=True )

        plot_cities_bars(df1, y_ax='aggregate_rating', n_top=7, agg_upper_cutoff=10, agg_lower_cutoff=agg_lower_cutoff)
        
        
    with col2.container():
        
#        n_top = 7
        
#        df_aux = df1[df1['aggregate_rating'] < 3]
#        df_aux = df_aux[['aggregate_rating', 'country_code', 'city']].groupby(by=['country_code', 'city']).count().reset_index()
#        df_aux['country'] = df_aux['country_code'].apply(country_name)
#        df_aux = df_aux.sort_values(by='aggregate_rating', ascending=False).reset_index(drop=True)
#        df_aux = df_aux.head(n_top)

#        histogram_option_x = 'city'
#        histogram_option_y = 'aggregate_rating'
#        column_depicted = histogram_option_x
#        y_axis = histogram_option_y
#        fig = px.bar( df_aux, x=column_depicted, y=y_axis, color='country', title='Top {} cidades com em número de restaurantes com avaliação média abaixo de 3'.format(n_top))
#        fig.update_layout(xaxis={'categoryorder':'total descending'})
#        st.plotly_chart( fig, use_container_width=True )

        plot_cities_bars(df1, y_ax='aggregate_rating', n_top=7, agg_upper_cutoff=agg_upper_cutoff, agg_lower_cutoff=-1)



with st.container():
        
#    n_top = 10
    
    
    
#    df_aux = df1[df1['aggregate_rating'] < 3]
#    df_aux = df1[['cuisines', 'country_code', 'city']].drop_duplicates().groupby(by=['country_code', 'city']).count().reset_index()
#    df_aux['country'] = df_aux['country_code'].apply(country_name)
#    df_aux = df_aux.sort_values(by='cuisines', ascending=False).reset_index(drop=True)
#    df_aux = df_aux.head(n_top)

#    histogram_option_x = 'city'
#    histogram_option_y = 'cuisines'
#    column_depicted = histogram_option_x
#    y_axis = histogram_option_y
#    fig = px.bar( df_aux, x=column_depicted, y=y_axis, color='country', title='Top {} cidades com mais tipos culinários'.format(n_top))
#    fig.update_layout(xaxis={'categoryorder':'total descending'})
#    st.plotly_chart( fig, use_container_width=True )
    
    plot_cities_bars(df1, y_ax='cuisines', n_top=n_top_cuisines, agg_upper_cutoff=10, agg_lower_cutoff=-1)
    
    
