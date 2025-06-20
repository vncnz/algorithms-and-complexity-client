import { VoronoiDiagram, Point } from './voronoi.js'

let computeVoronoi = (size) => {
    let points = [
        
        new Point(140,180),
        new Point(230,200),
        new Point(210,60),
        new Point(200,160),
        new Point(240,250),
        // new Point(size, size)
    ];

    let height = size;
    let width = size;

    // Create a new object
    let vor = new VoronoiDiagram(points, width, height);

    // Build the diagram
    vor.update();

    // Edges of the Voronoi diagram
    let edges = vor.edges.filter(el => !!el);
    // Vertices of the Voronoi diagram
    let vertices = vor.voronoi_vertex;

    return { edges, vertices, vor }
}

let extractPolygonsAndAdjacency = (edges) => {
    const idMap = new Map();  // Point → id univoco
    let nextId = 0;

    const polygons = new Map();     // id → lista di punti (vertici)
    const adjacency = new Set();    // string "i-j"

    for (const { start, end, arc: { left, right } } of edges) {
        // assegna id a left/right se ancora non mappati
        const lid = left != null
            ? (idMap.get(left) ?? idMap.set(left, nextId++).get(left))
            : null;
        const rid = right != null
            ? (idMap.get(right) ?? idMap.set(right, nextId++).get(right))
            : null;

        if (lid != null) {
            polygons.set(lid,
                (polygons.get(lid) || []).concat([start, end])
            );
        }
        if (rid != null) {
            polygons.set(rid,
                (polygons.get(rid) || []).concat([end, start])
            );
        }

        if (lid != null && rid != null) {
            const key = lid < rid ? `${lid}-${rid}` : `${rid}-${lid}`;
            adjacency.add(key);
        }
    }

    const finalPolygons = Array.from(polygons.entries()).map(
        ([id, pts]) => {
        const seen = new Set();
        const unique = pts.filter(p => {
            const k = `${p.x},${p.y}`;
            if (seen.has(k)) return false;
            seen.add(k);
            return true;
        });
        
        const site = {
            x: unique.map(p => p.x).reduce((sum, el) => sum + el) / unique.length,
            y: unique.map(p => p.y).reduce((sum, el) => sum + el) / unique.length
        }
        
        unique.sort((a,b) =>
            Math.atan2(a.y - site.y, a.x - site.x) - Math.atan2(b.y - site.y, b.x - site.x)
        );
        return { id, points: unique };
        }
    );

    const adjacencyPairs = Array.from(adjacency).map(k =>
        k.split("-").map(Number)
    );

    return { polygons: finalPolygons, adjacency: adjacencyPairs };
}

let data = computeVoronoi(500)
console.log('edges', data.edges)
console.log('vertices', data.vertices)
let vorResult = extractPolygonsAndAdjacency(data.edges)
console.log('vorResult', vorResult)


let color1 = 'hsl(0, 70%, 60%)'
let color2 = 'hsl(60, 70%, 50%)'
let color3 = "hsl(20, 40%, 50%)"
let color4 = "hsl(100, 40%, 50%)"
let colors = [color1, color2, color3, color4]

let p1 = [0,730]
let p2 = [384,730]
let p3 = [530,862]
let p4 = [0,50]
let p5 = [432,480]
let p6 = [240,670]
let p7 = [240,730]
let p8 = [534,382]
let p9 = [816,666]
let p10 = [624,862]
let p11 = [826,380]
let p12 = [1000,190]
let p13 = [1000,480]
let p14 = [430,0]
let p15 = [634,380]
let p16 = [720,290]

let polygons = [
    [p1, p2, p3, [0,862]],
    [p4, p5, p6, p7, p1],
    [p8, p9, p10, p3, p2, p7, p6],
    [p8, p11, p12, p13, p9],
    [p14, [1000,0], p12, p11, p15, p16],
    [p4, [0,0], p14, p16, p15, p8, p5],
    [p13, [1000,862], p10]
]

let near = [
    [0, 1],
    [0, 2],
    [1, 2],
    [1, 5],
    [2, 3],
    [2, 5],
    [2, 6],
    [3, 4],
    [3, 5],
    [3, 6],
    [4, 5]
]

/* VONOROI */
const dist = (a,b) => {
    // Esiste anche Math.hypot(a.x-b.x, a.y-b.y) ma non lo usa nessuno!
    let sqx = Math.pow(a.x-b.x, 2)
    let sqy = Math.pow(a.y-b.y, 2)
    return Math.pow(sqx+sqy, .5)
}
let circumcircle = (triangle) => {
  const [A,B,C] = triangle
  const D = 2*(A.x*(B.y-C.y) + B.x*(C.y-A.y) + C.x*(A.y-B.y))
  const Ux = ((A.x*A.x + A.y*A.y)*(B.y - C.y) + (B.x*B.x + B.y*B.y)*(C.y - A.y) + (C.x*C.x + C.y*C.y)*(A.y - B.y)) / D
  const Uy = ((A.x*A.x + A.y*A.y)*(C.x - B.x) + (B.x*B.x + B.y*B.y)*(A.x - C.x) + (C.x*C.x + C.y*C.y)*(B.x - A.x)) / D
  const center = {x: Ux, y: Uy}
  return {center, r: dist(center, A)}
}
let insideCircum = (p, tri) => {
  const {center, r} = circumcircle(tri)
  return dist(p, center) < r * (1 - 1e-6)
}
let edgeKey = (a,b) => {
  return [a.x,b.x,a.y,b.y].sort().join(',')
}
// ---------- Bowyer-Watson start ----------
let delaunay = (pts, W, H) => {
  const superTri = [
    {x: -W*10, y: -H*10},
    {x:  W*10, y: -H*10},
    {x: 0, y:  H*20}
  ];
  let triangles = [superTri];

  pts.forEach(p => {
    const bad = triangles.filter(tri => insideCircum(p, tri));
    const edgeCount = {};
    bad.forEach(tri => {
      [[tri[0],tri[1]], [tri[1],tri[2]], [tri[2],tri[0]]].forEach(([a,b]) => {
        const key = edgeKey(a,b);
        edgeCount[key] = edgeCount[key] ? null : [a,b]; // edge seen twice = shared = remove
      });
    });
    const borderEdges = Object.values(edgeCount).filter(e => e);
    triangles = triangles.filter(tri => !bad.includes(tri));
    triangles.push(...borderEdges.map(([a,b]) => [a,b,p]));
  });

  // Remove triangles using super triangle points
  return triangles.filter(tri => !tri.some(p => superTri.includes(p)));
}
// ---------- Bowyer-Watson end ------------

let clipPolygon = (polygon, {xMin, yMin, xMax, yMax}) => {
  const clip = (poly, inside, intersect) =>
    poly.reduce((out, p1, i) => {
      const p0 = poly[(i - 1 + poly.length) % poly.length];
      const i0 = inside(p0), i1 = inside(p1);
      if (i0 && i1) out.push(p1);
      else if (i0 && !i1) out.push(intersect(p0, p1));
      else if (!i0 && i1) out.push(intersect(p0, p1), p1);
      return out;
    }, []);

  let poly = polygon;
  poly = clip(poly, p => p.x >= xMin, (a, b) => intersectX(a, b, xMin));
  poly = clip(poly, p => p.x <= xMax, (a, b) => intersectX(a, b, xMax));
  poly = clip(poly, p => p.y >= yMin, (a, b) => intersectY(a, b, yMin));
  poly = clip(poly, p => p.y <= yMax, (a, b) => intersectY(a, b, yMax));
  return poly;
}

const intersectX = (a, b, x) => {
  const t = (x - a.x) / (b.x - a.x);
  return { x, y: a.y + t * (b.y - a.y) };
}
const intersectY = (a, b, y) => {
  const t = (y - a.y) / (b.y - a.y);
  return { x: a.x + t * (b.x - a.x), y };
}


const N = 20;

const generate = (N, size) => {

    const points = Array.from({length: N}, () => ({ 
        x: Math.random() * size, 
        y: Math.random() * size
    }));
    points.push({x: 0, y: 0})
    points.push({x: 0, y: size})
    points.push({x: size, y: size})
    points.push({x: size, y: 0})
    console.log('points', points)

    const triangles = delaunay(points, size, size)
    /*
    const cells = points.map(p => ({
        site: p,
        neighbors: new Set(),
        verts: []
    }));

    // Map from point to its cell
    const pointMap = new Map(points.map((p,i) => [p,i]));

    triangles.forEach(tri => {
        const cc = circumcircle(tri).center;
        tri.forEach((p, i) => {
            const i1 = (i+1)%3;
            const a = pointMap.get(p);
            const b = pointMap.get(tri[i1]);
            if (a != null && b != null) {
                cells[a].neighbors.add(b);
                cells[b].neighbors.add(a);
            }
            if (a != null) cells[a].verts.push(cc)
        })
    })

    return cells */

    const pointMap = new Map(points.map(p => [p, { site: p, tris: [] }]));

    triangles.forEach(tri => {
        tri.forEach(p => pointMap.get(p)?.tris.push(tri));
    });

    const bounds = { xMin: 0, yMin: 0, xMax: size, yMax: size }
    const cells = [...pointMap.values()].map(({site, tris}) => {
        let centers = tris.map(t => circumcircle(t).center);
        centers.sort((a,b) =>
            Math.atan2(a.y - site.y, a.x - site.x) - Math.atan2(b.y - site.y, b.x - site.x)
        );
        centers = clipPolygon(centers, bounds);
        return { site, polygon: centers };
    });
    return cells
}

// let triangles = generate(N, 500)
// console.log(triangles)

/* END */

export const createDefinitionForMapGame = (preferredSize) => {

    let game = {
        field: {
            width: preferredSize,
            height: preferredSize
        },
        playStatus: {
            status: 'running',
            progression: 0,
            internalData: {}
        },
        objects: {},
        events: {}
    }

    /* let triangles = generate(N, preferredSize)
    triangles.forEach((poly, idx) => {
        let id = `id${idx}`
        let locked = false
        game.objects[id] = {
            id,
            internalData: { locked, color: Math.floor(Math.random() * colors.length) },
            points: poly.polygon.map(p => { return [p.x, p.y] })// poly.map(p => `${p.x},${p.y}`).join(' ')
        }
        game.events[id] = locked ? [] : [ 'click', 'contextmenu' ]
    }) */
    /* Dubai polygons.forEach((poly, idx) => {
        let id = `id${idx}`
        let locked = false
        game.objects[id] = {
            id,
            internalData: { locked, color: Math.floor(Math.random() * colors.length) },
            points: poly.map(point => [point[0]/1000 * preferredSize, point[1]/862 * preferredSize])
        }
        game.events[id] = locked ? [] : [ 'click', 'contextmenu' ]
    }) */
    vorResult.polygons.forEach((poly, idx) => {
        let id = `id${idx}`
        let locked = false
        game.objects[id] = {
            id,
            internalData: { locked, color: Math.floor(Math.random() * colors.length) },
            points: poly.points.map(p => { return [p.x, p.y] })// poly.map(p => `${p.x},${p.y}`).join(' ')
        }
        game.events[id] = locked ? [] : [ 'click', 'contextmenu' ]
    })


    data.vertices.forEach((v, idx) => {
        let id = `v${idx}`
        let locked = false
        game.objects[id] = {
            id,
            internalData: { locked, color: 0 },
            points: [[v.x-5, v.y-5], [v.x+5, v.y-5], [v.x+5, v.y+5], [v.x-5, v.y+5]]
        }
        game.events[id] = locked ? [] : [ 'click', 'contextmenu' ]
    })


    drawField(game)
    game.playStatus.progression = 0
    return game
}

export const simulateServerForMapGame = (objid, evtType, input) => {
    console.warn('Simulating server input', objid, evtType, input)
    let output = JSON.parse(JSON.stringify(input)) // simulo una comunicazione col server quindi non modifico l'oggetto corrente, ovviamente!
    // let objid = objs[0]
    let obj = output.objects[objid]

    let isRightClick = evtType === 'click'
    let isLeftClick = evtType === 'contextmenu'
    if ((isRightClick || isLeftClick) && !obj.internalData.locked) {
        obj.internalData.color = (obj.internalData.color + 1) % colors.length
    }

    drawField(output)
    let win = checkWin(output)

    if (win) {
        output.playStatus.status = 'Win'
        output.events = {}
    }

    console.warn('Simulating server output', output)
    return output
}

const drawField = (output) => {
    Object.values(output.objects).forEach((obj, idx) => {
        obj.bgColor = colors[obj.internalData.color]
        obj.text = idx.toString()
    })
}

const checkWin = (output) => {
    let ok = true
    near.forEach(couple => {
        let c1 = Object.values(output.objects)[couple[0]].internalData.color
        let c2 = Object.values(output.objects)[couple[1]].internalData.color
        if (c1 == c2) {
            ok = false
        }
    })
    return ok
}