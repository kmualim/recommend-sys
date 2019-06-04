from bokeh.io import curdoc, output_notebook, show, push_notebook
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import PreText, MultiSelect, Slider, TableColumn, DataTable
#from ipywidgets import interact
from bokeh.models.callbacks import CustomJS
from bokeh.plotting import  output_file
import pandas as pd
from flask import Flask
from bokeh.client import pull_session
from bokeh.embed import server_session

data = pd.read_csv("metadata.csv", sep='\t')
#print(data.loc[0])
relevant_data = data[['Assay name', 'Biosample term name', 'Target of assay', 'Organism', 'Biosample treatment']]
ids_of_data=data['Accession']
# applying jaccard similarity
def jaccard_similarity(i,j):
    intersection = set(i).intersection(set(j))
    union = set(i).union(set(j))
    return len(intersection)/len(union)

def find_max_similarity(list_a):
  max_num = 0
  ids=[]
  list_a = list(map(float, list_a))
  for i in range(len(list_a)):
    if list_a[i]>max_num:
      max_num=list_a[i]
    if list_a[i]==max_num:
      ids.append(i)
  return ids, max_num


# get similarity matrix
sim_matrix = []
ids_matrix = []
def get_similarity_matrix(matrix):
  sim_matrix=[]
  scores=[]
  for i in range(len(matrix)):
    list_a=[]
    if i>0:
      list_a.append("0"*i)
    for j in range(i,len(matrix)):
      if i==j:
        list_a.append(-1)
      else:
        list_a.append(jaccard_similarity(matrix.loc[i], matrix.loc[j]))
    ids, max_num = find_max_similarity(list_a)
    ids_matrix.append(ids)
    scores.append({'similarity': max_num})
    sim_matrix.append(list_a)
  return sim_matrix, ids_matrix, scores

to_test = relevant_data[:6]
sim_matrix, ids_matrix, scores = get_similarity_matrix(to_test)
x=0
to_show = []
for i in ids_matrix:
  print("index", x)
  list_of_datasets=[]
  for j in range(len(i)):
    print(ids_of_data.loc[i[j]])
    list_of_datasets.append(ids_of_data.loc[i[j]])
  to_show.append({'datasets':list_of_datasets})
  x+=1
temp_col = pd.DataFrame(data=to_show)
other_temp = pd.DataFrame(data=scores)
#print(temp_col)
to_test['ids']=temp_col
to_test['similarity']=other_temp

source = ColumnDataSource(data=dict())
slider = Slider(title="similarity_threshold", value=0.0, start=0.0, end=1.0, step=0.1)

def update():
    current = to_test[to_test['similarity'] >= slider.value]
    source.data = {
        'similar'    : current.ids,
    }

slider.on_change('value', lambda attrname, old, new:update())

columns=[
    TableColumn(field="similar", title="Dataset IDs")
]

inputs=widgetbox(slider)
data_table = DataTable(source=source, columns=columns, width=800)
controls = column(slider)
layout=row(controls, data_table)
curdoc().add_root(row(controls, data_table))

update()
show(layout, notebook_handle=True)
