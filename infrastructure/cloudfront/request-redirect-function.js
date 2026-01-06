function handler(event) {
    var request = event.request;
    var uri = request.uri;

    // 1. If the user is looking for the waitlist, let them through
    if (uri.startsWith('/waitlist')) {
        return request;
    }

    // 2. If they are looking for anything else (like the home page), 
    // send them to the Google Bio site
    var response = {
        statusCode: 301,
        statusDescription: 'Moved Permanently',
        headers: {
            'location': { value: 'https://www.emeka.cloud' }
        }
    };

    return response;
}
