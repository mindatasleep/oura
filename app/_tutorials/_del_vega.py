import altair as alt
from vega_datasets import data

source = data.cars()


input_dropdown = alt.binding_select(options=['Europe','Japan','USA'])
selection = alt.selection_single(fields=['Origin'], bind=input_dropdown, name='Country of ')
color = alt.condition(selection,alt.Color('Origin:N', legend=None),alt.value('lightgray'))

# alt.Chart(source).mark_point().encode(
#     x='Horsepower:Q',
#     y='Miles_per_Gallon:Q',
#     color=color,
#     tooltip='Name:N'
# ).add_selection(
#     selection
# )




vega = alt.Chart(source).mark_circle(size=60).encode(
    x='Horsepower',
    y='Miles_per_Gallon',
    color=color,
).add_selection(
    selection
)




vega.save('a.html')