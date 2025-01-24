// Function to create word cloud
function createWordCloud() {
    // Clear previous word cloud
    const wordCloudContainer = d3.select("#wordCloud");
    wordCloudContainer.html("");
    
    // Add loading indicator
    const loadingDiv = wordCloudContainer
        .append("div")
        .style("text-align", "center")
        .style("padding", "20px")
        .text("Loading word cloud...");
    
    // Create container for word cloud
    const container = wordCloudContainer
        .append("div")
        .style("position", "relative")
        .style("width", "100%")
        .style("height", "400px")
        .style("background", "white")
        .style("border-radius", "8px")
        .style("overflow", "hidden")
        .style("display", "none");  // Hide initially

    // Fetch and display word cloud
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
            
            // Remove loading indicator
            loadingDiv.remove();
            
            // Show container
            container.style("display", "block");
            
            // Add the image
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

// Function to create price distribution histogram
function createPriceHistogram(prices) {
    // Clear previous histogram
    d3.select("#priceHistogram").html("");

    const margin = {top: 20, right: 20, bottom: 30, left: 50};
    const width = Math.min(600, window.innerWidth - 40) - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select("#priceHistogram")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleLinear()
        .domain([0, d3.max(prices)])
        .range([0, width]);

    const histogram = d3.histogram()
        .value(d => d)
        .domain(x.domain())
        .thresholds(x.ticks(30));

    const bins = histogram(prices);

    const y = d3.scaleLinear()
        .domain([0, d3.max(bins, d => d.length)])
        .range([height, 0]);

    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(10))
        .append("text")
        .attr("x", width/2)
        .attr("y", margin.bottom)
        .attr("fill", "currentColor")
        .attr("text-anchor", "middle")
        .text("Price ($)");

    svg.append("g")
        .call(d3.axisLeft(y))
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", -margin.left + 10)
        .attr("x", -height/2)
        .attr("fill", "currentColor")
        .attr("text-anchor", "middle")
        .text("Count");

    svg.selectAll("rect")
        .data(bins)
        .enter()
        .append("rect")
        .attr("x", d => x(d.x0))
        .attr("width", d => Math.max(0, x(d.x1) - x(d.x0) - 1))
        .attr("y", d => y(d.length))
        .attr("height", d => height - y(d.length))
        .style("fill", "#30a29a")
        .style("opacity", 0.7)
        .on("mouseover", function() {
            d3.select(this)
                .style("opacity", 1);
        })
        .on("mouseout", function() {
            d3.select(this)
                .style("opacity", 0.7);
        });
}

// Function to create property types bar chart
function createPropertyTypesChart(propertyTypes, counts) {
    // Clear previous chart
    d3.select("#propertyTypesChart").html("");

    const margin = {top: 20, right: 20, bottom: 90, left: 50};
    const width = Math.min(600, window.innerWidth - 40) - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select("#propertyTypesChart")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleBand()
        .range([0, width])
        .domain(propertyTypes)
        .padding(0.2);

    const y = d3.scaleLinear()
        .domain([0, d3.max(counts)])
        .range([height, 0]);

    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");

    svg.append("g")
        .call(d3.axisLeft(y));

    svg.selectAll("bars")
        .data(propertyTypes)
        .enter()
        .append("rect")
        .attr("x", d => x(d))
        .attr("y", (d, i) => y(counts[i]))
        .attr("width", x.bandwidth())
        .attr("height", (d, i) => height - y(counts[i]))
        .attr("fill", "#30a29a")
        .style("opacity", 0.7)
        .on("mouseover", function() {
            d3.select(this)
                .style("opacity", 1);
        })
        .on("mouseout", function() {
            d3.select(this)
                .style("opacity", 0.7);
        });
}

// Function to create room types pie chart
function createRoomTypesChart(roomTypes, counts) {
    // Clear previous chart
    d3.select("#roomTypesChart").html("");

    const width = Math.min(450, window.innerWidth - 40);
    const height = 400;
    const radius = Math.min(width, height) / 2;

    const svg = d3.select("#roomTypesChart")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width/2},${height/2})`);

    const color = d3.scaleOrdinal()
        .domain(roomTypes)
        .range(d3.schemeSet2);

    const pie = d3.pie()
        .value((d, i) => counts[i]);

    const arc = d3.arc()
        .innerRadius(0)
        .outerRadius(radius * 0.8);

    const outerArc = d3.arc()
        .innerRadius(radius * 0.9)
        .outerRadius(radius * 0.9);

    const arcs = svg.selectAll("arc")
        .data(pie(roomTypes))
        .enter()
        .append("g")
        .attr("class", "arc");

    arcs.append("path")
        .attr("d", arc)
        .attr("fill", d => color(d.data))
        .style("opacity", 0.7)
        .on("mouseover", function() {
            d3.select(this)
                .style("opacity", 1);
        })
        .on("mouseout", function() {
            d3.select(this)
                .style("opacity", 0.7);
        });

    // Add labels
    arcs.append("text")
        .attr("transform", d => {
            const pos = outerArc.centroid(d);
            return `translate(${pos})`;
        })
        .attr("dy", ".35em")
        .style("text-anchor", "middle")
        .text(d => `${d.data} (${counts[roomTypes.indexOf(d.data)]})`);
}

// Function to create amenities bar chart
function createAmenitiesChart(amenities, counts) {
    // Clear previous chart
    d3.select("#amenitiesChart").html("");

    const margin = {top: 20, right: 20, bottom: 30, left: 200};
    const width = Math.min(600, window.innerWidth - 40) - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select("#amenitiesChart")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const y = d3.scaleBand()
        .range([0, height])
        .domain(amenities)
        .padding(0.1);

    const x = d3.scaleLinear()
        .domain([0, d3.max(counts)])
        .range([0, width]);

    svg.append("g")
        .call(d3.axisLeft(y));

    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x));

    svg.selectAll("bars")
        .data(amenities)
        .enter()
        .append("rect")
        .attr("y", d => y(d))
        .attr("height", y.bandwidth())
        .attr("x", 0)
        .attr("width", (d, i) => x(counts[i]))
        .attr("fill", "#30a29a")
        .style("opacity", 0.7)
        .on("mouseover", function() {
            d3.select(this)
                .style("opacity", 1);
        })
        .on("mouseout", function() {
            d3.select(this)
                .style("opacity", 0.7);
        });
}

// Function to initialize all charts
function initializeCharts(data) {
    createWordCloud();
    if (data.prices && data.prices.length > 0) {
        createPriceHistogram(data.prices);
    }
    if (data.propertyTypes && data.propertyTypeCounts) {
        createPropertyTypesChart(data.propertyTypes, data.propertyTypeCounts);
    }
    if (data.roomTypes && data.roomTypeCounts) {
        createRoomTypesChart(data.roomTypes, data.roomTypeCounts);
    }
    if (data.topAmenities && data.amenityCounts) {
        createAmenitiesChart(data.topAmenities, data.amenityCounts);
    }
}
