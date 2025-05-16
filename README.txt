Render Hosting URL/Link:
      https://transposystem.onrender.com/

Note: MongoDB Atlas connection issue with Render

The connection to the MongoDB database is closing because the MongoDB client isn't being kept alive during the app's runtime on Render. Unlike on localhost, where the development server maintains an active connection, Render's production environment may terminate idle or unmanaged background tasks, leading to the database connection being closed unexpectedly.

This results in failed database queries and prevents full functionality of the website.
