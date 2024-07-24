from app import create_app

app = create_app()

if __name__ == "__main__":
    # Ensure the following block is within the application context
    app.run(debug=True, port=8000)
