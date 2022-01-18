import streamlit as st
import time
import numpy as np
import pandas as pd
from streamlit.elements.plotly_chart import SHARING_MODES
import sympy
from sympy.core.symbol import symbols
from sympy.solvers.diophantine.diophantine import descent, length
from sympy.solvers.solvers import solve
from db_fxns import create_table,add_data,view_all_data,view_unique_data,get_id,edit_well_id,delete_id
from db_fxns_aq import create_table_aq,view_all_data_aq,add_data_aq,view_unique_data_aq,get_id_aq,edit_aq_id, delete_id_aq
import base64
import pathlib
import matplotlib.pyplot as plt
from matplotlib import cm, colors
from matplotlib.patches import Rectangle
from matplotlib.ticker import StrMethodFormatter
import model_pro
import contrib
from PIL import Image


def app():

	#st.subheader("View Stored Values")
	results_aq = view_all_data_aq()
	results = view_all_data()

	#st.sidebar.markdown('---')
	#st.sidebar.markdown(""" **Stored Values:** """)
	
	'''if st.sidebar.checkbox("Show Stored Values"):
		st.subheader("Well Data")
		df = pd.DataFrame(results, columns=['Well ID', 'Pumping Rate', 'X-Coordinates', 'Y-Coordinates'])
		st.dataframe(df)	
		st.subheader("Aquifer Data")
		df_aq = pd.DataFrame(results_aq, columns=['Aquifer ID', 'Thickness', 'Base Flow', 'Porosity', 'Hydraulic Conductivity', 'Refernce Head'])
		st.dataframe(df_aq)'''

	#st.sidebar.markdown('---')
	
	st.title("Results According to Entered Values:")

	st.markdown("---")

	#menu = ["Wells", "Rivers", "No Flow"]
	#choice = st.sidebar.selectbox("Please Select Boundary Condition", menu)
	aem_model = model_pro.Model(k = results_aq[0][4], H = results_aq[0][1], h0 = results_aq[0][5], Qo_x=results_aq[0][2])
	if len(results) == 0:
		st.error("Please add atleast one Well")

	else:
		for j in range(6):
			if j == len(results):
				for i in range(j):
					well = model_pro.Well(aem_model, Q = results[i][1], rw = 0.2, x = results[i][2], y = results[i][3])

		c1, c2 = st.columns(2)

		
		xvec = np.linspace(0, 200, 100)
		yvec = np.linspace(0, 200, 100)

		xvec, yvec = np.meshgrid(xvec, yvec)

		h = []
		psi = []

		for x,y in zip(xvec.flatten(), yvec.flatten()):
			#st.write(x)
			#st.write(y)
			head = aem_model.calc_head(x,y)
			psi_0 = aem_model.calc_psi(x,y)
			#st.write(head)
			h.append(head)
			psi.append(psi_0)

		#st.write(h)

		h0 = np.array(h).reshape((100,100))
		psi0 = np.array(psi).reshape((100,100))
		#st.write(h)
		fig2, ax = plt.subplots(figsize = (10,10))
		contour = plt.contourf(xvec, yvec, h0, 15, cmap = cm.Blues)
		ax.set_xlabel('x [m]')
		ax.set_ylabel('y [m]')
		fig2.colorbar(contour, ax=ax, shrink = 0.9)

		contour_psi = plt.contour(xvec, yvec, psi0, 20, colors=('yellow',), linewidths = (2,))

		labels = ['Streamlines', 'Potential Lines']
		contour_psi.collections[6].set_label(labels[0])
		#contour.collections[7].set_label(labels[1])
		plt.legend(loc = "upper left")

		rect = Rectangle((0,0),2,200, linewidth=1, edgecolor='b', facecolor='b', zorder=2)
		ax.add_patch(rect)

		with c1:
			st.pyplot(fig2)

	#-------------------------------------------------------------------------------------------------------------------------------------

		solv = contrib.river_length(aem_model)

		#st.write("River capture length, Capture Position and Contribution to discharge is:")
		#st.write(solv.solve_river_length())

		length, riv_coords, capture_fraction = solv.solve_river_length()

		#st.write(length)

		xvec = np.linspace(0, 200, 100)
		yvec = np.linspace(0, 200, 100)

		xvec, yvec = np.meshgrid(xvec, yvec)

		h = []
		psi = []

		for x,y in zip(xvec.flatten(), yvec.flatten()):

			head = aem_model.calc_head(x, y)
			psi_0 = aem_model.calc_psi(x, y)

			h.append(head)
			psi.append(psi_0)

		h1 = np.array(h).reshape((100, 100))
		psi = np.array(psi).reshape((100, 100))

		fig3, ax = plt.subplots(figsize = (10, 10))
		contour = plt.contourf(xvec, yvec, h1, 15, cmap = cm.Blues, aplha = 0.7)
		ax.set_xlabel('x [m]')
		ax.set_ylabel('y [m]')
		fig3.colorbar(contour, ax=ax, shrink=0.9)

		contour_psi = plt.contour(xvec, yvec, psi, 20, colors=('yellow',), linewidths=(4,), linestyle=('-',))

		psi_0 = aem_model.calc_psi(0, riv_coords[0])
		psi_1 = aem_model.calc_psi(0, riv_coords[1])

		psi[((psi > psi_0-5) & (psi < psi_1+5))] = np.nan	

		rect = Rectangle((0,0),2,200, linewidth=1, edgecolor='b', facecolor='b', zorder=2)
		ax.add_patch(rect)

		contour_psi_river = plt.contour(xvec, yvec, psi, 40, colors=('darkred',), linewidths = (7,))

		river_capture = plt.plot([0,0], [riv_coords[0], riv_coords[1]], color='r', linestyle = '-', linewidth = 8)

		labels = ['Streamlines', 'Streamlines (Contribution)']
		contour_psi.collections[6].set_label(labels[0])
		contour_psi_river.collections[7].set_label(labels[1])
		plt.legend(loc = "upper left")

		st.sidebar.markdown("---")

		#----------------------------------------------------------------------------------------------------------------------------------------

		st.sidebar.title("Contribution Ratio:")

		if st.sidebar.checkbox(""" River Contribution to Discharge """):
			with c2:
				st.pyplot(fig3)

			ratio = capture_fraction*100
			r_ratio = ratio.round(decimals = 2)
			r_0 = riv_coords[1]
			r_1 = r_0.round(decimals = 2)

			
			st.sidebar.metric(label="River Capture Length", value = "%.2f m" %length)
			st.sidebar.metric(label="Contribution Ratio", value = "{} %".format(float(r_ratio)))
			st.sidebar.metric(label="Capture Position on y-axis", value = "%.2f & {} m".format(r_1) %riv_coords[0])

			st.markdown("---")	

		st.sidebar.markdown("---")
		st.sidebar.title("Time of Travel:")	
		if st.sidebar.checkbox("Travel Time of Water"):	
			tt = solv.time_travel(results_aq[0][3])
			#tt1 = np.amax(tt)
			#tt2 = np.amin(tt)
			tt1 = np.average(tt)
			tt2 = tt1.round(decimals=2)
			st.sidebar.metric(label="Travel Time of Water", value = "{} Days".format(tt2))
			

				

			


				
					

				
					
				
		
		
		
		dfh = pd.DataFrame(data = h0)
		df_psi = pd.DataFrame(data = psi0)
		dfh_rounded = dfh.round(decimals=3)
		df_psi_rounded = df_psi.round(decimals=3)
		csv = dfh_rounded.to_csv(sep="\t", index=False)
		csv_psi = df_psi_rounded.to_csv(sep="\t", index=False)
		#b64 = base64.b64encode(csv.encode()).decode()
		
		st.sidebar.markdown("---")	
		st.sidebar.title("Download \u03C8 & Head:")
		#st.sidebar.subheader("Download Head:")
		st.sidebar.download_button(label="Download H in CSV", data=csv, mime="csv")
		#st.sidebar.subheader("Download PSI:")
		st.sidebar.download_button(label="Download \u03C8 in CSV", data=csv_psi, mime="csv")

		
		

		

			





	
		

		
		

		
		
				

		


		




		
		
		



	st.sidebar.markdown("---")