# Floating Rate Loan Interest Service

A REST API that returns projected interest rates for a floating rate loan.

The project fetches 1-Month forward rates for SOFR dynamically from  
https://www.pensford.com/resources/forward-curve when a request comes in, and stores it in a SQLite database.  
The reason for choosing this database is that we are dealing with a small set of data with limited concurrent writes,  
so using a complete database server like PostgreSQL would be overkill in this case.

From the downloaded Excel file, the relevant sheet is 'Forward Curve', and only data from column G and H are used,  
starting from row 6 — which is the first entry. Here's how the first 5 rows look from the extracted dataframe:

|   | reset_date | rate    |
|---|------------|---------|
| 0 | 2025-06-24 | 0.043211 |
| 1 | 2025-07-24 | 0.042992 |
| 2 | 2025-08-24 | 0.042515 |
| 3 | 2025-09-24 | 0.041453 |
| 4 | 2025-10-24 | 0.040091 |

Interest rate for each month up to the given maturity date is calculated by adding the forward rate of each month with the  
given spread value. The sum is then bounded by the provided floor and ceiling values.  
The service has retry logic in place in case forward rate retrieval fails. After a certain number of attempts,  
it will fall back to using yesterday's data — since due to timezone differences, the current day might still be the previous one  
for the website that publishes the data.


### Instructions to run the service locally
1. Clone this repository to a folder on your local machine.  
2. In the terminal, go to the project directory and install the required libraries:  
   ```bash
   pip install -r requirements.txt
3. Run the service using command:
   ```bash
   uvicorn main:app --reload

### Instructions to run the service using Docker
1. Clone this repository to a folder on your local machine.
2. In case you don't have Docker on your machine, install it from-
    https://www.docker.com/products/docker-desktop/
3. Build Docker Image:
    ```bash
   docker build -t loan-rate-service .
4. Run Docker Container:
   ```bash
   docker run -d -p 8000:8000 --name loan-rate-container loan-rate-service
5. Check if it's running:
   - Go to http://localhost:8000/docs in your browser to see the Swagger UI.
   

### Test the endpoint
1. Go to Postman, select the POST method and enter the URL:
   - If testing with Docker:
      http://localhost:8000/loan-rate-curve
   - If testing without docker:
      http://127.0.0.1:8000/loan-rate-curve
2. In Headers, set
   - Key: Content-Type
   - Value: application/json
3. In Body, choose 'raw' and type JSON, then enter a sample like this:
   ```json
   {
       "maturity_date": "2025-12-01",
       "reference_rate": "SOFR",
       "rate_floor": 0.02,
       "rate_ceiling": 0.10,
       "rate_spread": 0.02
   }
4. You should get a 200 OK response with the result.


The suggested time to spend on this serve was 4 hrs, however I ended up spending around 5-6 hrs
because I wanted to make sure the service was clean, tested, and dockerized, and handling edge cases led me to make
a few changes.


### Future work:
1. Set up a scheduler to fetch the latest records daily at a fixed time, since forward 
rates on Pensford updates daily. 
2. Add secure user authentication to access the endpoint.
