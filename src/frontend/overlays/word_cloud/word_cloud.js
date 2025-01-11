class WordCloudOverlay extends OverlayClient {
    constructor(accessToken) {
        super('word_cloud', accessToken);
        this.words = new Map(); // word -> frequency
        this.svg = null;
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.maxWords = 50;
        this.colors = d3.schemeCategory10;
    }

    initialize() {
        this.svg = d3.select("#word-cloud")
            .attr("width", this.width)
            .attr("height", this.height)
            .append("g")
            .attr("transform", `translate(${this.width/2},${this.height/2})`);

        this.connect();
        window.addEventListener('resize', this.handleResize.bind(this));
    }

    handleMessage(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'chat') {
            this.processMessage(data.content);
        }
    }

    processMessage(message) {
        // Split message into words and count frequencies
        const words = message.toLowerCase()
            .replace(/[^\w\s]/g, '')
            .split(/\s+/)
            .filter(word => word.length > 3);

        words.forEach(word => {
            this.words.set(word, (this.words.get(word) || 0) + 1);
        });

        this.updateWordCloud();
    }

    updateWordCloud() {
        // Convert words map to array and sort by frequency
        const wordArray = Array.from(this.words.entries())
            .map(([text, size]) => ({
                text,
                size: Math.max(20, Math.min(100, size * 10))
            }))
            .sort((a, b) => b.size - a.size)
            .slice(0, this.maxWords);

        // Generate word cloud layout
        d3.layout.cloud()
            .size([this.width, this.height])
            .words(wordArray)
            .padding(5)
            .rotate(() => (~~(Math.random() * 2) - 1) * 45)
            .fontSize(d => d.size)
            .on("end", words => this.drawWordCloud(words))
            .start();
    }

    drawWordCloud(words) {
        const wordElements = this.svg.selectAll("text")
            .data(words, d => d.text);

        // Remove old words
        wordElements.exit()
            .attr("class", "word word-exit")
            .transition()
            .duration(1000)
            .style("opacity", 0)
            .remove();

        // Add new words
        wordElements.enter()
            .append("text")
            .attr("class", "word word-enter")
            .style("fill", (d, i) => this.colors[i % this.colors.length])
            .attr("text-anchor", "middle")
            .style("font-size", d => `${d.size}px`)
            .text(d => d.text)
            .merge(wordElements)
            .transition()
            .duration(1000)
            .style("font-size", d => `${d.size}px`)
            .attr("transform", d => `translate(${d.x},${d.y})rotate(${d.rotate})`);
    }

    handleResize() {
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        d3.select("#word-cloud")
            .attr("width", this.width)
            .attr("height", this.height);
        this.svg.attr("transform", `translate(${this.width/2},${this.height/2})`);
        this.updateWordCloud();
    }

    cleanup() {
        this.words.clear();
        if (this.svg) {
            this.svg.selectAll("*").remove();
        }
        super.cleanup();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get('token');
    
    if (accessToken) {
        const wordCloud = new WordCloudOverlay(accessToken);
        wordCloud.initialize();
    }
}); 