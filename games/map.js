import { VoronoiDiagram, Point , Edge } from './voronoi.js'

// TODO Bisogna considerare sul bordo anche i nodi che si trovano a 499.999999999999 se il bordo è 500 (javascript ed i floating points si odiano davvero!)
// TODO Bisogna sistemare il caso in cui vanno creati triangoli vicino ai vertici del campo di gioco perché con un edge unico non viene creato un poly
// * Può essere che convenga cambiare strategia ed anziché correggete i poligoni fare in modo che ci siano edges in più PRIMA di calcolare i poligoni

let computeVoronoi = (size) => {
    console.log('computeVoronoi', size)
    let points = [
        // new Point(size * 0.3, 0),
        // new Point(size * 0.7, 0),
        // new Point(size + 10, size * 0.5),
        // new Point(size * 0.5, size + 10),
        // new Point(-10, size * 0.5),

        new Point(140,180),
        new Point(230,200),
        new Point(210,60),
        new Point(200,160),
        new Point(250,250)
        // new Point(size, size)
    ]
    points.push(new Point(Math.random() * size, Math.random() * size))
    points.push(new Point(Math.random() * size, Math.random() * size))

    console.log('points', points)

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

let extractPolygonsAndAdjacency = (edges, size) => {
    const idMap = new Map();  // Point → id univoco
    let nextId = 0;

    const polygons = new Map();     // id → lista di punti (vertici)
    const adjacency = new Set();    // string "i-j"
    // const borderCells = new Set();

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
        }/* else {
            borderCells.add(rid);
        }*/
        if (rid != null) {
            polygons.set(rid,
                (polygons.get(rid) || []).concat([end, start])
            );
        }/* else {
            borderCells.add(lid);
        }*/

        if (lid != null && rid != null) {
            const key = lid < rid ? `${lid}-${rid}` : `${rid}-${lid}`;
            adjacency.add(key);
        }
    }
    // console.log('borders', borderCells)

    const finalPolygons = Array.from(polygons.entries()).map(
        ([id, pts]) => {
        const seen = new Set();
        let unique = pts.filter(p => {
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

        unique = completePoly(unique, size)

        return { id, points: unique };
        }
    );

    const adjacencyPairs = Array.from(adjacency).map(k =>
        k.split("-").map(Number)
    );

    return { polygons: finalPolygons, adjacency: adjacencyPairs };
}

let completePoly = (poly, size) => {
    // TODO: valutare se questa è la scelta migliore
    // ! Attenzione anche al fatto che funziona solo se ci sono poligoni incompleti con almeno due edges, il motivo è che un edge solo non crea un poly
    console.log('ppoly', poly)
    for (let i=0; i<poly.length; i++) {
        let p1 = poly[i]
        let p2 = poly[(i+1) % poly.length]
        console.log(p1, p2)
        if (p1.x === size && p2.y === size) {
            console.log('inserting bottom right')
            poly.splice(i+1, 0, new Point(size, size))
            i += 1
        } else if (p1.y === size && p2.x === 0) {
            console.log('inserting bottom left')
            poly.splice(i+1, 0, new Point(0, size))
            i += 1
        } else if (p1.x === 0 && p2.y === 0) {
            console.log('inserting top left')
            poly.splice(i+1, 0, new Point(0, 0))
            i += 1
        } else if (p1.y === 0 && p2.x === size) {
            console.log('inserting top right')
            poly.splice(i+1, 0, new Point(size, 0))
            i += 1
        } else if (p1.x === 0 && p2.x === size) {
            console.log('inserting top left+right')
            poly.splice(i+1, 0, new Point(0, 0))
            poly.splice(i+2, 0, new Point(size, 0))
            i += 2
        } else if (p1.y === 0 && p2.y === size) {
            console.log('inserting top+bottom right')
            poly.splice(i+1, 0, new Point(size, 0))
            poly.splice(i+2, 0, new Point(size, size))
            i += 2
        } else if (p1.x === size && p2.x === 0) {
            console.log('inserting bottom left+right')
            poly.splice(i+1, 0, new Point(size, size))
            poly.splice(i+2, 0, new Point(0, size))
            i += 2
        } else if (p1.y === size && p2.y === 0) {
            console.log('inserting top+bottom left')
            poly.splice(i+1, 0, new Point(0, size))
            poly.splice(i+2, 0, new Point(0, 0))
            i += 2
        }
    }
    return poly
}

let color1 = 'hsl(0, 70%, 70%)'
let color2 = 'hsl(60, 70%, 60%)'
let color3 = "hsl(20, 40%, 60%)"
let color4 = "hsl(100, 40%, 60%)"
let colors = [color1, color2, color3, color4]

export const createDefinitionForMapGame = (preferredSize) => {

    let data = computeVoronoi(500)
    // let edges = complete(data.edges.slice(), data.vertices, 500)
    const edges = data.edges
    console.log('edges', edges)
    console.log('vertices', data.vertices)
    let vorResult = extractPolygonsAndAdjacency(edges, 500)
    console.log('vorResult', vorResult)

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
    game.playStatus.internalData.adjacency = vorResult.adjacency

    /* edges.forEach((e, idx) => {
        let id = `e${idx}`
        let locked = false
        game.objects[id] = {
            id,
            internalData: { locked, color: 1 },
            points: [[e.start.x-5, e.start.y-5], [e.start.x+5, e.start.y-5], [e.end.x+5, e.end.y+5], [e.end.x-5, e.end.y+5]]
        }
    }) */

    /* data.vertices.forEach((v, idx) => {
        let id = `v${idx}`
        let locked = false
        game.objects[id] = {
            id,
            internalData: { locked, color: 0 },
            points: [[v.x-5, v.y-5], [v.x+5, v.y-5], [v.x+5, v.y+5], [v.x-5, v.y+5]]
        }
    }) */


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
    output.playStatus.internalData.adjacency.forEach(couple => {
        let c1 = Object.values(output.objects)[couple[0]].internalData.color
        let c2 = Object.values(output.objects)[couple[1]].internalData.color
        if (c1 == c2) {
            ok = false
        }
    })
    return ok
}