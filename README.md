# Recipe Manager

A Streamlit app for managing recipes. Add recipes, search by ingredient, browse and sort them, scale ingredients to any number of servings, get a random recipe, or see what you can cook with what you have at home.

- **Deployed app:** [ADD LINK HERE]
- **Video demo:** [ADD LINK HERE]

## Features

- **Add Recipe:** form with name, category, servings, ingredients, rating, prep time, steps and difficulty.
- **Search Recipe:** find recipes by ingredient.
- **View all:** table of all recipes, filter by category, sort by rating, and scale ingredients by servings.
- **Surprise me:** shows a random recipe.
- **What can I cook? (my own feature):** enter the ingredients you have and the app ranks recipes by match percentage and gives a shopping list for what's missing.

## Requirements completed

- CSV storage with an upload, edit and download loop.
- `st.session_state` holds recipes during the session.
- Categories (Breakfast, Lunch, Dinner, Dessert), 1-5 star ratings and sorting by rating.
- Ingredient scaling by servings.

## Run it

```
pip install streamlit pandas
streamlit run Recipe_manager.py
```

Upload `Recipe_manager.csv` in the sidebar, then press **Download CSV** after adding recipes to save them. Anything not downloaded is lost when the page reloads.

## Built with

Python, Streamlit, pandas