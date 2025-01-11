class WorldMapOverlay extends OverlayClient {
    constructor(accessToken) {
        super('world_map', accessToken);
        this.locationData = new Map(); // Store location frequencies
        this.svg = null;
        this.projection = null;
        this.path = null;
    }

    async initialize() {
        // Initialize D3 map
        this.svg = d3.select("#world-map")
            .append("svg")
            .attr("width", "100%")
            .attr("height", "100%");

        this.projection = d3.geoMercator()
            .scale(150)
            .translate([window.innerWidth / 2, window.innerHeight / 1.5]);

        this.path = d3.geoPath()
            .projection(this.projection);

        // Load world map data
        const worldData = await d3.json("https://unpkg.com/world-atlas@2/countries-110m.json");
        const countries = topojson.feature(worldData, worldData.objects.countries);

        // Draw base map
        this.svg.selectAll("path")
            .data(countries.features)
            .enter()
            .append("path")
            .attr("d", this.path)
            .attr("class", "country");

        await super.connect();
    }

    handleMessage(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'location') {
            this.highlightLocation(data.location);
        }
    }

    highlightLocation(location) {
        // Convert location to coordinates using geocoding service
        this.geocodeLocation(location).then(coords => {
            if (coords) {
                // Add heat point
                this.svg.append("circle")
                    .attr("class", "heat-point")
                    .attr("cx", this.projection(coords)[0])
                    .attr("cy", this.projection(coords)[1])
                    .attr("r", 5)
                    .transition()
                    .duration(3000)
                    .style("opacity", 0)
                    .remove();

                // Update heat map intensity
                this.updateHeatMap(coords);
            }
        });
    }

    async geocodeLocation(location) {
        try {
            const response = await fetch(
                `https://api.opencagedata.com/geocode/v1/json?q=${encodeURIComponent(location)}&key=YOUR_API_KEY`
            );
            const data = await response.json();
            if (data.results.length > 0) {
                const { lng, lat } = data.results[0].geometry;
                return [lng, lat];
            }
        } catch (error) {
            console.error('Geocoding error:', error);
        }
        return null;
    }

    updateHeatMap(coords) {
        const key = `${coords[0]},${coords[1]}`;
        const count = (this.locationData.get(key) || 0) + 1;
        this.locationData.set(key, count);

        // Update visualization based on frequency
        this.renderHeatMap();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get('token');
    
    if (accessToken) {
        const worldMap = new WorldMapOverlay(accessToken);
        worldMap.initialize();
    }
}); 