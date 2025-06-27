def explain_design_decisions():
    return """The endpoint is created using a TDD approach, having clean and clear nomenclature to understand what each 
    class and method is meant to do. The Controller class is the entry point that gets a POST request and responds 
    with the given list format. The Service class does the actual calculation to give the rates. The utility methods to 
    fetch, parse, and store data are done in the Util class methods. 
    
    It's assumed that the client will always want SOFR 1-month forward rates. I realised that the Pensford website 
    publishes data every day, however it's more aligned with USA timings. During the day when my service fetches its 
    latest available data, it's mostly yesterday's. Keeping this in mind, I've designed the service to retry fetching 
    the current day's sheet, and if it fails, it will fetch yesterday's data. The website has a repository for all 
    previous dates. This way, the service makes sure to get the latest data to perform calculations. Retry with 
    fallback is better than failing, in case the current day’s record is not yet available on the website. 
    
    SQLite is used for this service as the requirement is very light; it doesn't make sense to overhead with heavy 
    databases. To reduce the amount of writes to the store on each incoming request, it will first check if it 
    already stored the latest record, then it won’t write again. This is done assuming there will be multiple 
    requests throughout the day. 
    
    The service is dockerized with a test coverage of 84%.
    """


explain_design_decisions()
