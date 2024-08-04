import streamlit as st
import pandas as pd
import pydeck as pdk
import folium
import pickle
import requests
import gzip
import streamlit_folium as stf

from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from streamlit_option_menu import option_menu


#Streamlit Option Menu
selected = option_menu(None, ["Home", "Data Set", "Classification", 'Regression'], 
    icons=['house', 'table', "list-task", 'gear'], 
    menu_icon="cast", default_index=0, orientation="horizontal")
selected

#Home Menu
if selected == "Home":
    st.title("🌉 Golden Gate Estate")
    st.subheader("Your California Real Estate Partner.🏡")
    st.markdown("""
    ##### Property Valuation using Data Science
    
    At Golden Gate Estate, we recognize that your property is more than just a building; it's a home, an investment, and a part of your story. Our passion for real estate and our commitment to innovative technology have made us a leading estate agency in California.
    This app uses machine learning to predict the price of the house. It loads a pre-trained linear regression model, which takes as input various features of the house, such as the number of rooms, the number of bedrooms, the population of the house's neighborhood, 
    and the distance to the nearest city. The app preprocesses the input data by combining some of the features and adding new features, such as the distance to the nearest city.
    """)

elif selected == "Data Set":
    df = pd.read_csv('./sample_data/housing_new.csv')
    st.write("The Data Set as a table. ")
    st.markdown("📉[Data Set from kaggle](https://www.kaggle.com/datasets/camnugent/california-housing-prices/data)")
    st.table(df.head(41))
    
elif selected == "Classification":
    st.title("House Value Prediction")
    st.write("In this section you can add an address and the house price of your property will be estimated using the knn-model")
        
    #California Map
    california_map = folium.Map(location=[36.7783, -119.4179], zoom_start=6)
    
    #Enter address
    address = st.text_input("Enter an address in California", value="3410 Hillview Ave, Palo Alto, CA 94304")
    
    #Button to predict house value
    if st.button("Predict House Value"):
        
        #Geopy to change location into latitude, longitude
        geolocator = Nominatim(user_agent="streamlit_app.py")
        location = geolocator.geocode(address, addressdetails=True)
            
        with gzip.open('./models/class_model.pkl.gz', 'rb') as f:
            class_knn = pickle.load(f)
                    
        if location:
            latitude = location.latitude
            longitude = location.longitude
            state = location.raw.get("address", {}).get("state")

            if state == "California":
                house_value = class_knn.predict(pd.DataFrame([{"longitude": longitude, "latitude": latitude}]))
                st.write(f"Geschätzter House Value in California: {house_value[0]}")
            else:
                st.write("Die Adresse liegt nicht in Kalifornien.")
                    
            #Show California Map
            if latitude and longitude:
                folium.Marker([latitude, longitude], tooltip=address).add_to(california_map)
                st.write("Location on California Map:")
                folium_static(california_map)
        else:
            st.write("Adresse nicht gefunden.")
                          
elif selected == "Regression":
    st.title("Using a regression to predict california house prices")
    address = st.text_input("Enter an address in California", value="3410 Hillview Ave, Palo Alto, CA 94304")
    median_income = st.number_input("Median Income")
    total_rooms = st.number_input("Total Rooms")
    
    #California Map
    california_map = folium.Map(location=[36.7783, -119.4179], zoom_start=6)

    #Make sure that address is not empty before retrieving the coordinates
    if address and st.button("Predict House Value"):
        #Change coordinates into address using geopy
        geolocator = Nominatim(user_agent="streamlit_app.py")
        location = geolocator.geocode(address, addressdetails=True)
            
        with gzip.open('./models/reg_model.pkl.gz', 'rb') as f:
            reg_rfr = pickle.load(f)

        if location:
            latitude = location.latitude
            longitude = location.longitude
            state = location.raw.get("address", {}).get("state")

            if state == "California":
                st.session_state.latitude = latitude
                st.session_state.longitude = longitude

                #show address on the map
                folium.Marker([latitude, longitude], tooltip=address).add_to(california_map)
                
                latitude = st.session_state.latitude
                longitude = st.session_state.longitude

                #predict the house value
                prediction = reg_rfr.predict(pd.DataFrame([{"longitude": longitude, "latitude": latitude, "median_income": median_income, "total_rooms": total_rooms}]))
                st.write(f"Estimated House Value: {prediction[0]}" "$")

            else:
                st.write("Die eingegebene Adresse liegt nicht in Kalifornien.")
        else:
            st.write("Adresse nicht gefunden.")

    #show the map in streamlit
    stf.folium_static(california_map)

