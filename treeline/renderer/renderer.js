class AdaptiveRenderer {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            webglThreshold: 10000,
            chunkSize: 1000,
            ...options
        };

        this.renderer = null;
        this.mode = null;
    }

    async initialize(graphData) {
        const nodeCount = graphData.nodes.length;
        const hasWebGL = this._checkWebGLSupport();

        if (hasWebGL && nodeCount > this.options.webglThreshold) {
            console.log('Using WebGL renderer for large graph');
            this.renderer = new WebGLRenderer(this.container, this.options);
            this.mode = 'webgl';
        } else {
            console.log('Using D3 renderer');
            this.renderer = new OptimizedD3Renderer(this.container, this.options);
            this.mode = 'd3';
        }

        await this.renderer.initialize(graphData);
        return this.mode;
    }

    _checkWebGLSupport() {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
        return !!gl;
    }
}

class WebGLRenderer {
    constructor(container, options) {
        this.container = container;
        this.options = options;
        this.gl = null;
        this.program = null;
        this.data = null;

        this.lastFrameTime = 0;
        this.frameCount = 0;
    }

    async initialize(graphData) {
        const canvas = document.createElement('canvas');
        canvas.width = this.container.clientWidth;
        canvas.height = this.container.clientHeight;
        this.container.appendChild(canvas);

        this.gl = canvas.getContext('webgl2');
        if (!this.gl) throw new Error('WebGL2 not supported');

        await this._initShaders();
        this._initBuffers(graphData);
        this._startRenderLoop();
    }

    _initShaders() {
        const vertexShader = this.gl.createShader(this.gl.VERTEX_SHADER);
        this.gl.shaderSource(vertexShader, `#version 300 es
            in vec2 position;
            in vec3 color;
            in float size;

            uniform mat4 viewMatrix;
            uniform vec2 viewport;

            out vec3 fragColor;

            void main() {
                gl_Position = vec4(position / viewport * 2.0 - 1.0, 0.0, 1.0);
                gl_PointSize = size;
                fragColor = color;
            }
        `);
        this.gl.compileShader(vertexShader);

        const fragmentShader = this.gl.createShader(this.gl.FRAGMENT_SHADER);
        this.gl.shaderSource(fragmentShader, `#version 300 es
            precision highp float;
            in vec3 fragColor;
            out vec4 outColor;

            void main() {
                vec2 coord = gl_PointCoord - vec2(0.5);
                float r = length(coord) * 2.0;
                float alpha = 1.0 - smoothstep(0.8, 1.0, r);
                outColor = vec4(fragColor, alpha);
            }
        `);
        this.gl.compileShader(fragmentShader);

        this.program = this.gl.createProgram();
        this.gl.attachShader(this.program, vertexShader);
        this.gl.attachShader(this.program, fragmentShader);
        this.gl.linkProgram(this.program);
    }

    _initBuffers(graphData) {
        const positions = new Float32Array(graphData.nodes.length * 2);
        const colors = new Float32Array(graphData.nodes.length * 3);
        const sizes = new Float32Array(graphData.nodes.length);

        graphData.nodes.forEach((node, i) => {
            positions[i * 2] = node.x || 0;
            positions[i * 2 + 1] = node.y || 0;

            const color = this._getNodeColor(node.type);
            colors[i * 3] = color[0];
            colors[i * 3 + 1] = color[1];
            colors[i * 3 + 2] = color[2];

            sizes[i] = node.size || 5.0;
        });

        this._createBuffer('position', positions);
        this._createBuffer('color', colors);
        this._createBuffer('size', sizes);
    }

    _createBuffer(name, data) {
        const buffer = this.gl.createBuffer();
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, buffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, data, this.gl.STATIC_DRAW);

        const location = this.gl.getAttribLocation(this.program, name);
        this.gl.enableVertexAttribArray(location);
        this.gl.vertexAttribPointer(
            location,
            name === 'position' ? 2 : name === 'color' ? 3 : 1,
            this.gl.FLOAT,
            false,
            0,
            0
        );
    }

    _startRenderLoop() {
        const render = (timestamp) => {
            this.frameCount++;
            if (timestamp - this.lastFrameTime >= 1000) {
                const fps = this.frameCount;
                this.frameCount = 0;
                this.lastFrameTime = timestamp;
                console.log(`WebGL Renderer FPS: ${fps}`);
            }

            this.gl.clear(this.gl.COLOR_BUFFER_BIT);
            this.gl.drawArrays(this.gl.POINTS, 0, this.data.nodes.length);
            requestAnimationFrame(render);
        };

        requestAnimationFrame(render);
    }

    _getNodeColor(type) {
        const colors = {
            module: [0.2, 0.4, 0.8],
            class: [0.8, 0.2, 0.4],
            function: [0.2, 0.8, 0.4],
            default: [0.5, 0.5, 0.5]
        };
        return colors[type] || colors.default;
    }
}

class OptimizedD3Renderer {
    constructor(container, options) {
        this.container = container;
        this.options = options;
        this.simulation = null;
        this.quadtree = null;
        this.visibleNodes = new Set();
    }

    async initialize(graphData) {
        const svg = d3.select(this.container)
            .append('svg')
            .attr('width', '100%')
            .attr('height', '100%');

        // chunking the nodes to avoid blocking the main thread
        const processChunk = (start) => {
            const end = Math.min(start + this.options.chunkSize, graphData.nodes.length);
            const chunk = graphData.nodes.slice(start, end);

            this.simulation.nodes(chunk);

            if (end < graphData.nodes.length) {
                setTimeout(() => processChunk(end), 0);
            }
        };

        this.simulation = d3.forceSimulation()
            .force('link', d3.forceLink().id(d => d.id))
            .force('charge', d3.forceManyBody().strength(-30))
            .force('center', d3.forceCenter(
                this.container.clientWidth / 2,
                this.container.clientHeight / 2
            ));

        processChunk(0);

        this._setupViewportCulling(svg, graphData);
    }

    _setupViewportCulling(svg, graphData) {
        this.quadtree = d3.quadtree()
            .x(d => d.x)
            .y(d => d.y)
            .addAll(graphData.nodes);

        svg.call(d3.zoom().on('zoom', () => {
            this._updateVisibleNodes();
        }));

        this._updateVisibleNodes();
    }

    _updateVisibleNodes() {
        const visible = new Set();
        const bounds = this.container.getBoundingClientRect();

        this.quadtree.visit((node, x1, y1, x2, y2) => {
            if (!node.length) {
                do {
                    const d = node.data;
                    if (d.x >= bounds.left && d.x <= bounds.right &&
                        d.y >= bounds.top && d.y <= bounds.bottom) {
                        visible.add(d.id);
                    }
                } while (node = node.next);
            }
            return x1 > bounds.right || x2 < bounds.left ||
                   y1 > bounds.bottom || y2 < bounds.top;
        });

        this.visibleNodes = visible;
        this._renderVisibleNodes();
    }

    _renderVisibleNodes() {
        d3.selectAll('.node')
            .style('display', d => this.visibleNodes.has(d.id) ? null : 'none');
    }
}

export { AdaptiveRenderer };
