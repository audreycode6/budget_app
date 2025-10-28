# Import factory + db from package
from budget_app import create_app, db

app = create_app()

if __name__ == "__main__":
    # debug=True here is fine for dev, but be careful in production
    app.run(debug=True, port=5003)