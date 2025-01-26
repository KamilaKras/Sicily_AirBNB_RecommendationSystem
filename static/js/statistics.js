// tworzenie chmury slow
function createWordCloud() {
    // czyszczenie poprzedniej chmury
    const wordCloudContainer = d3.select("#wordCloud");
    wordCloudContainer.html("");
    
    // dodanie paska ładowania
    const loadingDiv = wordCloudContainer
        .append("div")
        .style("text-align", "center")
        .style("padding", "20px")
        .text("Loading word cloud...");
    
    // kontener dla chmury slow
    const container = wordCloudContainer
        .append("div")
        .style("position", "relative")
        .style("width", "100%")
        .style("height", "400px")
        .style("background", "white")
        .style("border-radius", "8px")
        .style("overflow", "hidden")
        .style("display", "none");  

    // wyswietlanie chmury slow
    fetch('/static/data/wordcloud_data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (!data.image) {
                throw new Error('No image data found');
            }
            
            // usuniecie paska ładowania
            loadingDiv.remove();
            
            // pokazanie kontenera
            container.style("display", "block");
            
            // dodanie obrazka
            container.append("img")
                .attr("src", `data:image/png;base64,${data.image}`)
                .style("width", "100%")
                .style("height", "100%")
                .style("object-fit", "contain");
        })
        .catch(error => {
            console.error('Error loading word cloud:', error);
            loadingDiv
                .text("Error loading word cloud. Please try refreshing the page.");
        });
}

// wywolanie chmury
function initializeCharts(data) {
    createWordCloud();
    if (data.prices && data.prices.length > 0) {
        createPriceHistogram(data.prices);
    }
}