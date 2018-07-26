#--------------KPN----------------
#Script created by @Daniël Homburg
#This script is used to create a graph visualization based on the questions in the intake form.
#Without the intake form this script is useless, therefore make contact with 
#the owner of the script: 		@Daniël Homburg  (daniel.homburg@hotmail.com)
#or the owner of the service: 	@Michael Loanjoe (michael.loanjoe@kpn.com)
#before using the script.

import pandas, csv, os

from flask import Flask, make_response, request, send_file, url_for
from graphviz import Digraph



#This function checks if the edge is already created
def is_in_list(x,y):
	for z in y:
		if z == x:
			return True
	return False


#This function return all nodes that are created in a dictionary
def get_all_nodes(columns,extra_columns,input_file):
	nodes = {}

	data = pandas.read_csv(input_file,delimiter=";") 
	unique_columns = set(columns + extra_columns)
	
	for x in unique_columns:
		function = "data." + x + ".tolist"
		column_values = list(set(list(data[x])))
		clean_column_values = [x for x in column_values if str(x) != 'nan']
		nodes[x] = clean_column_values
		
	return (nodes)
	

#This is a helper function to apply the styles on the graph
def apply_styles(graph, styles):
    graph.graph_attr.update(
        ('graph' in styles and styles['graph']) or {}
    )
    graph.node_attr.update(
        ('nodes' in styles and styles['nodes']) or {}
    )
    graph.edge_attr.update(
        ('edges' in styles and styles['edges']) or {}
    )
	
    return graph

def get_special_person_data(input_file):
	data = pandas.read_csv(input_file,delimiter=";") 
	return (data["Persoonsgegeven"][data["Bijzonderpersoonsgegeven"] != "ONWAAR"].tolist())


def get_form_value(graph_param,key,alternative):
	if key in graph_param:
		return (graph_param[key])
	return (alternative)


def create_visualization(input_file,graph_param):

	#Config
	output_file_graph = "static/" + get_form_value(graph_param,"file_name","result") 
	used_columns = get_form_value(graph_param,"used_coloms","DataSubjects,Persoonsgegeven,DataBron,NaamInformatievoorziening,Hoofdbedrijfsproces").split(",")
	extra_columns = get_form_value(graph_param,"extra_coloms","DataEigenaar,DataBron").split(",")
	figures = get_form_value(graph_param,"figures","oval,folder,rectangle,rect,cds").split(",")
	
	#Create start of graph file	
	dot = Digraph(format=get_form_value(graph_param,"graph_format","pdf"))

	#Set the style of the graph
	styles = {
		'graph': {
			'labelloc': 't',
			'label': get_form_value(graph_param,"title",""),
			'bgcolor': get_form_value(graph_param,"graph_background_color","#333333"),
			'rankdir': get_form_value(graph_param,"rankdir","BT"),
			'ranksep': get_form_value(graph_param,"ranksep","5"),
			'nodesep': get_form_value(graph_param,"nodesep","2"),
			'fontname': 'Times',
			'fontcolor': get_form_value(graph_param,"graph_font_color","white"),
		},
		'nodes': {
			'fontname': 'Times',
			'fontcolor': get_form_value(graph_param,"node_font_color","white"),
			'color': 'white',
			'fillcolor': get_form_value(graph_param,"node_fill_color","#006699"),
			'style':  get_form_value(graph_param,"node_style","filled"),
		
		},
		'edges': {
			'color': get_form_value(graph_param,"edge_color","white"),
			'arrowhead': get_form_value(graph_param,"edge_arrowhead","open"),
			'fontname': 'Times',
		}
	}

	#Create dictionary with all items that become nodes
	nodes = get_all_nodes(used_columns,extra_columns,input_file)

	#Set the style for all nodes -> this can be set with the list "figures"
	special_person_data = get_special_person_data(input_file)
	label_nc = get_form_value(graph_param,"label_nc","_nd")
	for x in used_columns + extra_columns:
		for y in nodes[x]:
			if label_nc in y.lower():
				dot.node(y, label = "niet duidelijk", style =  get_form_value(graph_param,"style_nc","dotted"))


	counter = 0
	for x in used_columns:
		for y in nodes[x]:
			if label_nc not in y.lower():
				if y in special_person_data:
					dot.node(y, shape=figures[counter], fillcolor = get_form_value(graph_param,"specific_data_color","#E92C03"),style =  'filled')
				else:
					dot.node(y, shape=figures[counter])
		counter += 1

	
	
	#Fill graph file with nodes + edges
	i = 1
	graph_list = []
	used_columns_indexes = []
	extra_columns_indexes = []
	
	#Open csv file	
	with open(input_file, 'r') as f:
		reader = csv.reader(f)
		input_csv = list(reader)

	#For every Row, create edges between nodes if they do not already exist
	for x in input_csv:
		#Split the rows
		row_split = x[0].split(";")
		
		#Handle the headers
		if i == 1:
			
			for y in used_columns:
				used_columns_indexes.append(row_split.index(y))
				
			for y in extra_columns:
				extra_columns_indexes.append(row_split.index(y))
				
			i = i + 1
			
			continue
		
		
		#Handle the columns 
		for y in range(0,len(used_columns_indexes)-1):
			first_element = row_split[used_columns_indexes[y]]
			second_element = row_split[used_columns_indexes[y+1]]
			edge = '"' + first_element + '"' + " -> " + '"' + second_element + '";'
			
			if not is_in_list(edge,graph_list):
				graph_list.append(edge)
				dot.edge(first_element,second_element)
			
		for y in range(0,len(extra_columns_indexes)-1):
			first_element = row_split[extra_columns_indexes[y]]
			second_element = row_split[extra_columns_indexes[y+1]]
			edge = '"' + first_element + '"' + " -> " + '"' + second_element + '";'
			
			if not is_in_list(edge,graph_list):
				graph_list.append(edge)
				dot.edge(first_element,second_element)

			
	#Apply the style on the graph
	dot = apply_styles(dot, styles)

	#Render the graph to the output_file_graph
	dot.render(output_file_graph, view=False)
	print ("Created graph.. Stored as: " + output_file_graph + "." + get_form_value(graph_param,"graph_format","pdf"))



# Initialize the Flask application
app = Flask(__name__, static_url_path='')

@app.route('/')
def form():
    return """
        <html>
	    <style>
    		{ margin: 0; padding: 0; }

		table{
		    width: 50%;
		    margin-left: auto;
		    margin-right: auto;
		}

   		html { 
     		    background: url('background.jpg') no-repeat center center fixed; 
    		    -webkit-background-size: cover;
   		    -moz-background-size: cover;
  		    -o-background-size: cover;
  		    background-size: cover;
		}

		body {
		    color: white;
		}
		#submit_button {
		    margin: auto 0;
		    text-align: center;
		}
	    </style>
            <body>
                <h1 align="center">Visualisatie Tool</h1>

                <form action="/create_visualization" method="post" enctype="multipart/form-data">
		<table>
		  <tr>
		    <th><label for="title">Upload de CSV:</label></th>
		    <th><input type="file" name="input_file" /></th>	
                  </tr>
		  <tr>
		    <th><label for="title">Titel van de Graph:</label></th>
		    <th><input type="text" name="title"/></th>	
                  </tr>
		  <tr>
		    <th><label for="graph_background_color">Graph achtergrond kleur:</label></th>
		    <th><input type="text" name="graph_background_color" value="#333333"/></th>	
                  </tr>  
 		  <tr>
		    <th><label for="used_columns">Geef namen van de kolommen:</label></th>
		    <th><input type="text" name="used_columns" value="DataSubjects,Persoonsgegeven,DataBron,NaamInformatievoorziening,Hoofdbedrijfsproces"/></th>	
                  </tr> 
 		  <tr>
		    <th><label for="figures">Welke figuren moeten de kolommen krijgen?:</label></th>
		    <th><input type="text" name="figures" value="oval,folder,rectangle,rect,cds"/></th>	
                  </tr> 
 		  <tr>
		    <th><label for="extra_columns">Geef de namen van kolommen zonder figuur:</label></th>
		    <th><input type="text" name="extra_columns" value="DataEigenaar,DataBron"/></th>	
                  </tr>
 		  <tr>
		    <th><label for="label_nc">Label voor aangeven onduidelijkheid:</label></th>
		    <th><input type="text" name="label_nc" value="_nd"/></th>	
                  </tr>
 		  <tr>
		    <th><label for="style_nc">Style bij het niet duidelijk zijn:</label></th>
		    <th><input type="text" name="style_nc" value="dotted"/></th>	
                  </tr>
 		  <tr>
		    <th><label for="specific_data_color">Kleur bij speciale persoonsgegevens:</label></th>
		    <th><input type="text" name="specific_data_color" value="#E92C03"/></th>	
                  </tr>
		  <tr>
		    <th><label for="rankdir">Graph direction:</label></th>
		    <th><input type="text" name="rankdir" value="BT"/></th>	
                  </tr>
 		  <tr>
		    <th><label for="ranksep">Graph rank seperation:</label></th>
		    <th><input type="text" name="ranksep" value="5"/></th>	
                  </tr>
 		  <tr>
		    <th><label for="nodesep">Node seperation:</label></th>
		    <th><input type="text" name="nodesep" value="2"/></th>	
                  </tr>
 		  <tr>
		    <th><label for="graph_font_color">Graph font color:</label></th>
		    <th><input type="text" name="graph_font_color" value="white"/></th>	
                  </tr>
 		  <tr>
		    <th><label for="node_font_color">Node font color:</label></th>
		    <th><input type="text" name="node_font_color" value="white"/></th>	
                  </tr>
 		  <tr>
		    <th><label for="node_fill_color">Node fill color:</label></th>
		    <th><input type="text" name="node_fill_color" value="#006699"/></th>	
                  </tr>
 		  <tr>
		    <th><label for="node_style">Node style:</label></th>
		    <th><input type="text" name="node_style" value="filled"/></th>	
                  </tr>
 		  <tr>
		    <th><label for="edge_color">Edge color:</label></th>
		    <th><input type="text" name="edge_color" value="white"/></th>	
                  </tr>
 		  <tr>
		    <th><label for="edge_arrowhead">Edge arrow style:</label></th>
		    <th><input type="text" name="edge_arrowhead" value="open"/></th>	
                  </tr>
 		  <tr>
		    <th><label for="graph_format">Graph format:</label></th>
		    <th><input type="text" name="graph_format" value="pdf"/></th>	
                  </tr>
		   <tr>
		    <th><label for="file_name">Graph file name:</label></th>
		    <th><input type="text" name="file_name" value="result"/></th>	
                  </tr>
		</table>
		<div id="submit_button">
		<th><input type="submit" value="Maak Visualisatie!" align="center"/></th>	
		</div>
                </form>
            </body>
        </html>
    """

@app.route('/create_visualization', methods=["POST"])
def main_program_view():

    # Input file
    file = request.files['input_file']

    if not file:
        return "Geen bestand geselecteerd!"
    else:
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        filename_path = os.path.join(THIS_FOLDER, file.filename)
        file.save(os.path.join("/home/graphviz/", file.filename))
        create_visualization(filename_path, request.form)

    return (""" <html> 
		<head>
		    
		<style>
    		    { margin: 0; padding: 0; }

   		html { 
     		    background: url('background.jpg') no-repeat center center fixed; 
    		    -webkit-background-size: cover;
   		    -moz-background-size: cover;
  		    -o-background-size: cover;
  		    background-size: cover;
		}

		body {
		    color: white;
		}

		input.d_button {
		  width: 300px;
		  padding: 20px;
		  cursor: pointer;
		  font-weight: bold;
		  font-size: 150%;
		  background: #3366cc;
		  color: #fff;
		  border: 1px solid #3366cc;
		  border-radius: 10px;
		}
		input.d_button:hover {
		  color: #ffff00;
		  background: #000;
		  border: 1px solid #fff;
		}
		#download_button {
		  display: inline-block;
    		  position: fixed;
    		  top: 0;
    		  bottom: 0;
    		  left: 0;
    		  right: 0;
    		  width: 200px;
    		  height: 100px;
    		  margin: auto;

	    </style>
            <body>
		<div id=download_button><form>
		   <input class="d_button" type="button" value="Download Visualisatie"
			onclick="window.location.href='/""" + get_form_value(request.form,"file_name","result") + """.""" + get_form_value(request.form,"graph_format","pdf") + """'"/>
		</form>
		</div>
	    </body>
	    </html>""")


    

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')
