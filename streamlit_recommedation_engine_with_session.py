##############################################################################################

# This file contain Streamlit dashboard for recommendation engine
# pip install streamlit
# RUN : streamlit run streamlit_recommedation_engine.py
##############################################################################################

import streamlit as st 
import streamlit.components.v1 as stc
from recommendation_engine import Recommendation_Engine
import SessionState
import os
from datetime import datetime
import numpy as np
import cv2
from scorecard_generation import Scorecard_generator

HTML_TITLE = """
	<div style="background-color:#D4EFDF;padding:10px;border-radius:10px">
	<h1 style="color:#1E8449;text-align:center;">Fitbit4Food</h1>
	</div>
	"""

# create object of our backend script
recommendation_engine = Recommendation_Engine()

# create object of score card generator backend
scorecard_obj = Scorecard_generator()

session_state = SessionState.get(page_number = 0)

@st.cache
def save_image(file):
	#if file is too large then return
	if file.size > 209715200: # 200 MB
		return 1
	
	folder = "public_receipt_images"
	datetoday = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	
	# clear the folder to avoid storage overload (will use when required)
	# for filename in os.listdir(folder):
	# 	file_path = os.path.join(folder, filename)
	# 	try:
	# 		if os.path.isfile(file_path) or os.path.islink(file_path):
	# 			os.unlink(file_path)
	# 	except Exception as e:
	# 		print('Failed to delete %s. Reason: %s' % (file_path, e))

	try:
		with open("log0.txt", "a") as f:
			f.write(f"{file.name} - {file.size} - {datetoday};\n")
	except:
		pass

	with open(os.path.join(folder, file.name), "wb") as f:
		f.write(file.getbuffer())
	return 0


# GUI function for dashboard
def recommendation_engine_gui():
	
	# initialize menu and add to visual HTML(Front End)
	menu = ["Home","Scan receipt"]
	choice = st.sidebar.selectbox("Options",menu)

	# initialize preference_option and add to visual HTML(Front End)
	preference_option = ["All", "Organic", "Non GMO", "Pesticide Free", "Free Range", "Nut Free", "Dairy Free", "Palm Oil Free", "Additives Free", "Sugar Free", "Gluten Free", "Vegan", "Halal", "None"]
	my_preference_preset = 'None'

	# preset user profile
	preset = ["None", "Healthy Helena", "Sustainable Sally", "Dietary Dave", "Price Conscious Peter", "Only Organic Tessa"]
	user_preset = st.sidebar.selectbox("Preset User Profile",preset)

	# Title 'NLP based recommendation engine' into HTML
	stc.html(HTML_TITLE)

	# Select All Preferences option
	if user_preset == "Healthy Helena":
		my_preference_preset = ["Additives Free", "Sugar Free", "Additives Free", "Dairy Free", "Gluten Free", "Vegan"]
	elif user_preset == "Sustainable Sally":
		my_preference_preset = ["Organic", "Free Range", "Vegan", "Non GMO", "Palm Oil Free", "Pesticide Free"]
	elif user_preset == "Dietary Dave":
		my_preference_preset = ["Halal", "Vegan", "Gluten Free", "Dairy Free", "Sugar Free", "Additives Free"]
	elif user_preset == "Only Organic Tessa":
		my_preference_preset = ["Organic"]
	else:
		pass

	# Set user preference
	my_preference = st.sidebar.multiselect("Set your preferences (priority wise)", preference_option, default=my_preference_preset)

	if "All" in my_preference:
		my_preference = ["Organic", "Non GMO", "Pesticide Free", "Free Range", "Nut Free", "Dairy Free", "Palm Oil Free", "Additives Free", "Sugar Free", "Gluten Free", "Vegan", "Halal"]

	# Merge preferences  
	if len(my_preference) != 0 :
		if len(user_preset) != 0:
			my_preference = ' '.join(my_preference) + ' ' + ' '.join(my_preference_preset)
		else:
			my_preference = ' '.join(my_preference)
	else:
		if len(user_preset) != 0:
			my_preference = ' '.join(my_preference_preset)
		else:
			my_preference = ' '
	my_preference = my_preference.lower()
	# Home option
	if choice == "Home":

		# initialize sorting option and add to visual HTML(Front End)
		sort_option = ["Relevance", "Price Low to High","Price High to Low", "Unit Price Low to High"]
		sort_by = st.sidebar.selectbox("Sort By", sort_option)
		
		# set sub header
		st.subheader("Search Product")

		# Take user input
		product_name = st.text_input("Enter Product name")
		
		# initialize and add search button into HTML
		submit = st.button('Search')

		# Enable mouse click or keyboard "enter / return " key to search product
		if submit or product_name:
			
			if product_name.strip() == '':
				if my_preference != '':
					final_keyword = my_preference 
				else: 
					final_keyword = ''
					
			else:
				final_keyword = product_name.lower()

			# Get recommendation using our object (Only single function call)
			# TODO: ADD GUI for empty_flag if product list is empty
			print("my_preference",my_preference)
			recommendations, len_of_list, empty_flag = recommendation_engine.recommendations_from_keyword(final_keyword, THRESHOLD= 2, USER_PREFERENCE_TEXT= my_preference)

			# Condition if user input is empty -> pass user preference  
			if final_keyword.strip() == '':
				TOTAL_PRODUCTS = """
					<div style="background-color:#464e5e;padding:10px;border-radius:10px">
					<h3 style="color:white;text-align:center;">Please enter product name  "{product_name}":  About <b>{len_of_list}</b> products recommended </h3>
					</div>
					""".format(len_of_list = len_of_list, product_name = '')

			else:			# Condition else user input is merged with user preference
				TOTAL_PRODUCTS = """
					<div style="background-color:#464e5e;padding:10px;border-radius:10px">
					<h3 style="color:white;text-align:center;">Results for "{product_name}":  About <b>{len_of_list}</b> products recommended </h3>
				</div>
					""".format(len_of_list = len_of_list, product_name = final_keyword)
			
			# Display 'Results for...' tag into html 
			stc.html(TOTAL_PRODUCTS, height = 100)

			# Manage sorting option
			if sort_by == 'Price Low to High':
				recommendations = recommendations.sort_values(by=['Product Price'], ascending=True)
			elif sort_by == 'Price High to Low':
				recommendations = recommendations.sort_values(by=['Product Price'], ascending=False)
			elif user_preset == 'Price Conscious Peter' or sort_by == 'Unit Price Low to High':
				recommendations = recommendations.sort_values(by=['price per base volume'], ascending=True)
			else:
				pass

			# uncomment this to see dataframe without html
			#st.dataframe(data=recommendations)
			
			try: 
				# HTML + logic to display list of product
				# Number of entries per screen
				N = 15

				# A variable to keep track of which product we are currently displaying
				#page_number = 0

				last_page = len(recommendations) // N

				# Add a next button and a previous button
				prev, _ , page_reset , _ , next = st.beta_columns([1,2,2,2,1])

				if next.button("Next"):

					if session_state.page_number + 1 > last_page:
						session_state.page_number = 0
					else:
						session_state.page_number += 1

				if prev.button("Previous"):

					if session_state.page_number - 1 < 0:
						session_state.page_number = last_page
					else:
						session_state.page_number -= 1

				if page_reset.button("Reset Page"):
					session_state.page_number = 0
				else:
					pass

				# Get start and end indices of the next page of the dataframe
				start_idx = session_state.page_number * N 
				end_idx = (1 + session_state.page_number) * N

				CURRENT_PAGE = """
					<div style="background-color:#464e5e;padding:1px;border-radius:1px">
						<h4 style="color:white;text-align:center;vertical-align:middle;"> Current Page: "{current_page}" </h4>
					</div>
						""".format(current_page=session_state.page_number)

				# Display current page
				page = stc.html(CURRENT_PAGE, height = 60)

				# Index into the sub dataframe
				sub_recommendations = recommendations.iloc[start_idx:end_idx]
				
				# uncomment this line to see sub list
				#st.write(sub_recommendations)

				# Select required column
				myrows = zip(sub_recommendations['URL'], sub_recommendations['Product Title'], sub_recommendations['Product Image'], sub_recommendations['Product Price'])

				for _, (col1,col2,col3,col4) in enumerate(myrows):
					# create HTML product card
					PRODUCT_CARD = '''
					<div style="background-color:#464e5e;padding: var(--su-4);border-radius:10px;position: relative;">
					
					<span class="column" style="background-color: rgb(49, 51, 63);float: left;
					width: 40%;height: 192px;
					padding: 10px;position: relative; justify-content: center;">
						<img style="color:white;text-align:right;" alt = "image"  src ='{img_link}' width="200" height="200">
						
					</span>
					
					
					<span class="column" style="background-color: rgb(49, 80, 63);float: left;
					width: 54%; padding: 10px;position: relative; height: 192px;justify-content: center; ">
						<h2 style = "color:white;">{title}</h2>
						<h3 style = "color:white;">$ {price}</h3>
						<a target="_blank" href="{product_link}" style = "background-color:rgb(48, 200, 0);color:white;padding:10px; border-radius:10px"> Buy Now </a>
					</span>
					
					</div>
					'''.format(product_link = col1, img_link = col3, title = col2, price = col4)
					
					stc.html(PRODUCT_CARD,height=250)

			except Exception as e:
				print(e)
				pass

	elif choice == "Scan receipt":
		# init variable image_arr
		image_arr = None
		st.subheader("Scan your receipt")
		image_file = st.file_uploader("Upload receipt image file", type=['jpg', 'png', 'jpeg'])
		if image_file is not None:
			# folder public_receipt_images contains all images from public upload
			if not os.path.exists("public_receipt_images"):
				os.makedirs("public_receipt_images")
			path = os.path.join("public_receipt_images", image_file.name)
			if_save_image = save_image(image_file)
			if if_save_image == 1:
				st.warning("File size is too large. Try another file with lower size.")
			elif if_save_image == 0:
				
				# display receipt
				try:
					# st.image(image_file, use_column_width=True)
					image_arr = cv2.imread(path, 0)
				except Exception as e:
				 	st.error(f"Error {e} - wrong format of the file. Try another .jpg file.")
			else:
				st.error("Unknown error")
		else:
			if st.button("Try test file"):
				# st.image("1.jpeg", use_column_width=True)
				image_file = "1.jpeg"
				image_arr = cv2.imread(image_file, 0)

		if image_arr is not None:
			# one function call to access everything
			output_score, image = scorecard_obj.get_score_from_receipt(image_arr, USER_PREFERENCE_TEXT= my_preference)
			st.write("Scanned image")
			st.image(image, use_column_width=True)
			print("output_score", output_score)
			#st.text(output_score)

			progress_bar = st.progress(0)

			# add animation of fill
			for i in range(output_score):
				# Update progress bar upto output score.
				progress_bar.progress(i + 1)
			
			# display score 
			SCORE_TITLE = """
			<div style="background-color:#464e5e;padding:10px;border-radius:10px">
			<h1 style="color:white;text-align:center;">{output_score} %</h1>
			<h3 style="color:white;text-align:center;"> is your shopping score </h3>
			</div>
			""".format(output_score= output_score)

			st.balloons()
			stc.html(SCORE_TITLE)

# main function
if __name__ == '__main__':
	recommendation_engine_gui()
