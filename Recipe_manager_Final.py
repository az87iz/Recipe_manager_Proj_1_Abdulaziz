import pandas as pd
import streamlit as st

# page title in the browser tab + a little icon
st.set_page_config(page_title="Recipe Manager", page_icon="🍳")

COLUMNS = ["Recipe_name", "Recipe_Category", "Ingredients", "Prep_time",
           "Servings", "Cooking_Instructions", "Difficulty_level", "rating"]

if "recipes" not in st.session_state:
    # first visit: start with an empty table
    st.session_state.recipes = pd.DataFrame(columns=COLUMNS)

# upload box in sidebar
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])
# only load the file once
if uploaded_file is not None and st.session_state.get("loaded_file") != uploaded_file.file_id:
    loaded = pd.read_csv(uploaded_file)
    # if the CSV is missing a column, add it empty so nothing breaks later
    for col in COLUMNS:
        if col not in loaded.columns:
            loaded[col] = None
    # keep only columns
    st.session_state.recipes = loaded[COLUMNS]
    # remember file 
    st.session_state.loaded_file = uploaded_file.file_id

recipes_df = st.session_state.recipes


def scale_ingredients(ingredients_text, old_servings, new_servings):
    # how much bigger or smaller the recipe needs to be
    factor = new_servings / old_servings
    new_list = []

    # split the saved ingredient text at each comma
    for item in str(ingredients_text).split(","):
        item = item.strip()
        number = ""
        # collect the digits at the start and stop at the first letter
        for ch in item:
            if ch.isdigit() or ch == ".":
                number += ch
            else:
                break

        if number:
            # scale the number and add the rest of the text back
            new_list.append(f"{float(number) * factor:g}" + item[len(number):])
        else:
            # no number (ex."salt"), keep  as is
            new_list.append(item)

    return new_list


# sidebar nav menu
with st.sidebar:
    current_page = st.radio(
        "Recipe Manager",
        ("Add Recipe", "Search Recipe", "View all", "Surprise me", "What can I cook?")
    )
    st.divider()

# ADD RECIPE
if current_page == "Add Recipe":
    st.title("Add a Recipe!")
    # a form holds everything until the user presses Submit
    with st.form("my_form", clear_on_submit=True):
        st.write("What are we cooking today?")
        Recipe = st.text_input("Recipe Name.")
        # dropdown for the category
        Recipe_category = st.selectbox(
            "Category",
            options=["Breakfast", "Lunch", "Dinner", "Dessert"],
        )
        # how many people the recipe feeds (used for scaling)
        base_servings = st.number_input(
            "How many servings does this recipe make?",
            min_value=1
        )
        # ingredients typed as one line, split on commas into a list
        Ingredients = st.text_input(
            "Enter the ingredients for this recipe!",
            placeholder="eg: 0.5kg water, 1L milk, 3g Cheese..."
        ).split(",")

        st.write("Rate this recipe out of 5!")
        selected = st.feedback("stars", key="rating")
        if selected is not None:
            selected += 1   # shift to 1-5 stars

        Prep = st.number_input("How long does it take to cook this recipe?", step=0.20)

        st.write("Insert the step by step instructions on how to cook this recipe!")
        # one step per line turned into a list of steps
        Cook_inst = st.text_area("Cooking instructions (one step per line)").splitlines()

        diff = st.selectbox(
            "What is the difficulty level of this recipe?",
            ("Easy", "Medium", "Hard"),
        )
        submitted = st.form_submit_button("Submit")

        if submitted:
            if not Recipe.strip():
                st.error("Please enter a recipe name.")
            else:
                # build a one-row table for the new recipe
                new_table = pd.DataFrame(
                    {
                        "Recipe_name": [Recipe],
                        "Recipe_Category": [Recipe_category],
                        # save ingredients as plain text: "a, b, c"
                        "Ingredients": [", ".join(i.strip() for i in Ingredients if i.strip())],
                        "Prep_time": [Prep],
                        "Servings": [base_servings],
                        # save steps as plain text: "step 1 | step 2"
                        "Cooking_Instructions": [" | ".join(s.strip() for s in Cook_inst if s.strip())],
                        "Difficulty_level": [diff],
                        "rating": [selected]
                    }
                )
                # stick the new row onto the bottom of the saved recipes
                st.session_state.recipes = pd.concat(
                    [st.session_state.recipes, new_table], ignore_index=True
                )
                st.success(f"Added '{Recipe}'! Download the CSV from the sidebar to save it.")

##SEARCH
if current_page == "Search Recipe":
    st.title("Search for a recipe")
    # .strip() removes spaces
    Search_ingr = st.text_input(
        "Enter an ingredient and we'll match you up with a recipe to cook!"
    ).strip()

    if Search_ingr:
        # keep rows whose ingredients contain the search word (ignoring capitals)
        matches = recipes_df[
            recipes_df["Ingredients"]
            .astype(str)
            .str.contains(Search_ingr, case=False, na=False, regex=False)
        ]

        if matches.empty:
            st.info(f"No recipes found with '{Search_ingr}'.")
        else:
            # show only the needed columns
            st.table(
                matches[
                    ["Recipe_name", "Ingredients", "Prep_time", "Difficulty_level"]
                ]
            )

## VIEW ALL
if current_page == "View all":
    st.title("All recipes")

    # creates two dropdowns next to each other
    c1, c2 = st.columns(2)
    category = c1.selectbox(
        "Filter by category",
        ["All", "Breakfast", "Lunch", "Dinner", "Dessert"]
    )
    order = c2.selectbox(
        "Sort by rating",
        ["Highest first", "Lowest first"]
    )

    # work on a copy so the saved recipes stay untouched
    view = recipes_df.copy()
    
    if category != "All":
        # keep only the chosen category
        view = view[view["Recipe_Category"] == category]
    # sort by rating, and put unrated recipes at the bottom
    view = view.sort_values("rating", ascending=(order == "Lowest first"), na_position="last")
    st.table(view.reset_index(drop=True))

    # scaling section
    st.divider()
    st.subheader("Scale a recipe")
    if view.empty:
        st.info("No recipes to scale.")
    else:
        pick = st.selectbox("Pick a recipe", view["Recipe_name"].tolist())
        # check the row of the recipe that is picked
        row = view[view["Recipe_name"] == pick].iloc[0]
        # fall back to 1 if servings is missing or zero
        old_servings = int(row["Servings"]) if pd.notna(row["Servings"]) and row["Servings"] > 0 else 1
        new_servings = st.number_input("Servings you want", min_value=1, value=old_servings)
        st.write("**Ingredients:**")
        # show each ingredient with its new amount
        for ing in scale_ingredients(row["Ingredients"], old_servings, new_servings):
            st.write(f"- {ing}")

## SURPRISE ME
if current_page == "Surprise me":
    st.title("Surprise Me!")

    if st.button("Pick a Random Recipe"):
        if recipes_df.empty:
            st.info("No recipes available yet. Add a recipe first!")
        else:
            # pick one random row
            rand_rec = recipes_df.sample(n=1).iloc[0]

            st.subheader(rand_rec["Recipe_name"])
            st.write(f"**Prep Time:** {rand_rec['Prep_time']}")
            st.write(f"**Difficulty:** {rand_rec['Difficulty_level']}")

            st.write("**Ingredients:**")
            # one bullet per ingredient
            for ing in str(rand_rec["Ingredients"]).split(","):
                st.write(f"- {ing.strip()}")

            st.write("**Cooking Instructions:**")
            # numbered steps (separated by " | ")
            for n, step in enumerate(str(rand_rec["Cooking_Instructions"]).split(" | "), 1):
                st.write(f"{n}. {step}")

### WHAT CAN I COOK? (my extra feature)
if current_page == "What can I cook?":
    st.title("What can I cook?")
    st.caption("List what's in your kitchen and I'll rank your recipes by how many ingredients you already have.")
    pantry_text = st.text_input("Your ingredients (comma-separated)", placeholder="eg: eggs, milk, flour")
    # clean list of what the user has, all lowercase for easy matching
    pantry = [p.strip().lower() for p in pantry_text.split(",") if p.strip()]

    if pantry:
        if recipes_df.empty:
            st.info("No recipes yet. Add one first!")
        else:
            results = []
            # check every recipe one by one
            for _, r in recipes_df.iterrows():
                # clean list of this recipe's ingredients
                ings = [i.strip().strip("'\"") for i in str(r["Ingredients"]).strip("[]").split(",") if i.strip()]
                # ingredients the user already has (partial match, so "egg" matches "3 eggs")
                have = [i for i in ings if any(p in i.lower() for p in pantry)]
                # everything else goes on the shopping list
                missing = [i for i in ings if i not in have]
                # percentage of the recipe the user can already make
                match = round(100 * len(have) / len(ings)) if ings else 0
                results.append({
                    "Recipe": r["Recipe_name"],
                    "Match %": match,
                    "You have": ", ".join(have),
                    "Shopping list": ", ".join(missing) or "Nothing, you're set!",
                })
            out = pd.DataFrame(results)
            # hide 0% matches and show the best matches first
            out = out[out["Match %"] > 0].sort_values("Match %", ascending=False)
            if out.empty:
                st.info("No recipes use those ingredients.")
            else:
                st.table(out.reset_index(drop=True))

# download button 
st.sidebar.download_button(
    "Download CSV",
    st.session_state.recipes.to_csv(index=False).encode("utf-8"),
    file_name="Recipe_manager.csv",
    mime="text/csv"
)