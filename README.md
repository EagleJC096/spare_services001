# Project 1

Web Programming with Python and JavaScript

---Book Look---

    --Python Files--

        ::application.py::
        Application.py controls all routes. Also contains all of the raw SQL code that interacts with the database.

        ::helpers.py::
        Only contains the decorate routes function to require a user to login to access certain pages. (http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/)

        ::import.py::
        File used to import books.csv into database. Iterates over every line of the csv and inserts the data into the appropriate rows.

    --Templates--

        ::layout.html::
        Provides the main body of HTML5 for each page. Inludes nav-bars.

        ::index.html::
        Includes a search box and explanation for the website. The search box is used to search for books by isbn #, title, or author.

        ::login.html::
        Allows the user to log in.

        ::register.html::
        Prompts the user to input a username and a password as well as a password confirmation.

        ::results.html::
        Lists a table of books returned by the search query. Includes isbn #, title, author, and a button to goto that book.

        ::book.html::
        Lists the book title, author, year, goodreads data, and any reviews for that book. Also allows the user to submit his own review.
    
    --Static Files--

        ::book.jpg::
        The logo for Book Look as shown on the navbar

        ::main.css::
        The css used for all of the website. Includes navbar controls, and goodreads databox formatting, among other things.

        ::full_form.css::
        Overrides the .form-control {width: auto} in main.css for the form that allows a user to submit a review on book.html so that the form's width is 100%.
