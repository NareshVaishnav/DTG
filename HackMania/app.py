from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import folium
from flask_cors import CORS
from flask_pymongo import PyMongo
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

app.config['MONGO_DBNAME'] = 'Hackmania'
app.config['MONGO_URI'] = 'mongodb+srv://nareshvaishnavrko11:nareshrko11@cluster0.hudqzdr.mongodb.net/Hackmania'
client = MongoClient('mongodb+srv://nareshvaishnavrko11:nareshrko11@cluster0.hudqzdr.mongodb.net/')
mongo = PyMongo(app)

@app.route('/map', methods=['GET', 'POST'])
def display_map():

    if request.method == 'POST':
        district = request.form['district'].strip()

        # Query the MongoDB database for the latitude and longitude of the given district
        # and store the results in a list of dictionaries
        locations = list(mongo.db.users.find({'district': district, 'latitude': {'$exists': True}, 'longitude': {'$exists': True}}, {'_id': 0, 'latitude': 1, 'longitude': 1}))
        
        if not locations:
            return render_template('map.html', district=district, error='No records found for this district.')
        
        # Create a Folium map centered on the first location in the list
        map = folium.Map(location=[locations[0]['latitude'], locations[0]['longitude']], zoom_start=10)
        
        # Add markers for all the locations in the list
        for location in locations:
            # Query the MongoDB database for the user information
            user_info = mongo.db.users.find_one({'district': district, 'latitude': location['latitude'], 'longitude': location['longitude']})
            
            # Create the URL for the farmer's profile using the farmer's ID
            # profile_url = url_for('farmer_profile', farmer_id = str(user_info['_id']))
            
            # Modify the popup HTML to include the "More Info" link leading to the farmer's profile
            popup_html = f"""
            <div style="width: 300px;">
                <h3 style="margin: 0; padding: 10px; background-color: #00704A; color: #FFF; text-align: center; font-size: 20px;">
                    {user_info['full-name']}
                </h3>
                <div style="padding: 10px;">
                    <p style="margin: 0; margin-bottom: 5px; font-size: 16px;">Phone: {user_info['phone']}</p>
                    <p style="margin: 0; margin-bottom: 5px; font-size: 16px;">Land Size: {user_info['landsize']} acres</p>
                </div>
            </div>
            """  # Add a marker with the pop-up to the map
            folium.Marker(location=[location['latitude'], location['longitude']], popup=popup_html).add_to(map)
        
        # Convert the map to HTML and pass it to the template
        map_html = map._repr_html_()
        return render_template('mindex.html', district=district, map_html=map_html)

    # If the request method is not 'POST', return the default map page
    return render_template('mindex.html', district='', map_html='', error='')

if __name__ == '__main__':
    app.run(port=5500, debug=True)
