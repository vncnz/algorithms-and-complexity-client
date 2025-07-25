/* const game = {
    field: {
        xsize: 10,
        ysize: 10
    },
    objects: [id:{
        id: 1,
        bgColor: "rgb(200 0 0)",
        fgColor: 'lime',
        rect: { x: 4, y: 6, w: 3, h: 2 },
        text: 'A'
    }, {
        id: 2,
        bgColor: "rgb(0 0 200 / 50%)",
        fgColor: 'yellow',
        rect: { x: 3, y: 4, w: 2, h: 3 },
        text: 'B',
        events: [ 'click' ]
    }],
    events: {
        'all' or object id: evt_types
    }
} */

import { createDefinitionForFlipGame, simulateServerForFlipGame } from '/games/flip.js'
import { createDefinitionForMinesweeperGame, simulateServerForMinesweeperGame } from '/games/minesweeper.js'
import { createDefinitionForMapGame, simulateServerForMapGame } from '/games/map.js'

const gameManagement = {
    flip: {
        createDefinition: createDefinitionForFlipGame,
        simulateServer: simulateServerForFlipGame
    },
    minesweeper: {
        createDefinition: createDefinitionForMinesweeperGame,
        simulateServer: simulateServerForMinesweeperGame
    },
    map: {
        createDefinition: createDefinitionForMapGame,
        simulateServer: simulateServerForMapGame
    }
}
let gameServer = null
let game = null
let size = 500

const chooseGame = choosen => {
    console.log('chooseGame')
    gameServer = choosen
    game = gameServer.createDefinition(size)
    draw()
    bindEvents()
}

let createSvgChild = (type, attrs, content) => {
    let elm = document.createElementNS('http://www.w3.org/2000/svg', type)
    for (const [key, value] of Object.entries(attrs)) {
        elm.setAttribute(key, value)
    }
    if (content) elm.innerHTML = content
    return elm
}

let computeCentroid = points => {
    // https://en.wikipedia.org/wiki/Centroid
    const len = points.length;
    let area = 0
    let c = {
        x: 0,
        y: 0
    }
    for (let i = 0; i < len; i++) {
        const p0 = points[i]
        const p1 = points[(i+1)%len] // Considering all sides!
        const p0x = p0[0]
        const p0y = p0[1]
        const p1x = p1[0]
        const p1y = p1[1]
        const a = p0x * p1y - p1x * p0y;
        area += a
        c.x += (p0x + p1x) * a
        c.y += (p0y + p1y) * a
    }
    area /= 2
    if (area === 0) {
        return points[0]
    }
    c.x /= (6 * area)
    c.y /= (6 * area)
    return c
}


let draw = () => {
    const svg = document.querySelector('svg')
    if (!svg) return
    // ctx.font = "20px Arial";
    svg.innerHTML = ""
    svg.setAttribute("width", size)
    svg.setAttribute("height", size)

    // const rect = svg.getBoundingClientRect()
    // const xpx = rect.width / game.field.xsize
    // const ypx = rect.height / game.field.xsize

    svg.setAttribute("viewBox", `0 0 ${game.field.width} ${game.field.height}`)

    Object.values(game.objects).forEach(obj => {
        let rect = createSvgChild('polygon', {
            points: obj.points.map(p => `${p[0]},${p[1]}`).join(' '),
            id: obj.id,
            fill: obj.bgColor || "transparent",
            stroke: 'gray'
        })
        svg.appendChild(rect)

        if (obj.text) {
            // Version 1: for simple polygons bbox center will be ok
            // let bbox = rect.getBBox()
            // const tx = bbox.x + bbox.width/2
            // const ty = bbox.y + bbox.height/2

            // Version 2: for semi-complex polygons (coo avg)
            // const tx = obj.points.map(p => p[0]).reduce((sum, el) => sum + el) / obj.points.length
            // const ty = obj.points.map(p => p[1]).reduce((sum, el) => sum + el) / obj.points.length

            // Version 3: using centroid
            let c = computeCentroid(obj.points)


            let text = createSvgChild('text', {
                x: c.x,
                y: c.y,
                style: 'pointer-events: none'
            }, obj.text)
            svg.appendChild(text)
            // let w = ctx.measureText(obj.text).width
            //ctx.fillText(obj.text, tx - w/2, ty + w/2)
        }
    })

    let to_output = [game.playStatus.status]
    if (game.playStatus.progressionText) { to_output.push(`(${game.playStatus.progressionText})`) }
    if (game.playStatus.progression) { to_output.push(`(${Math.round(game.playStatus.progression * 100)}%)`) }
    document.querySelector('#game-status').innerHTML = to_output.join(' ')
    // ctx.fillStyle = "rgb(200 0 0)";
    // ctx.fillRect(10, 10, 50, 50);

    // ctx.fillStyle = "rgb(0 0 200 / 50%)";
    // ctx.fillRect(30, 30, 50, 50);
}

let bindEvents = () => {
    for (const [key, value] of Object.entries(game.events)) {
        let elm = document.getElementById(key)
        if (elm) {
            value.forEach(evtType => {
                elm.addEventListener(evtType, evt => {
                    evt.preventDefault()
                    game = gameServer.simulateServer(key, evtType, game)
                    draw()
                    bindEvents()
                })
            })
        }
    }
}

chooseGame(gameManagement.map)
new Array(...document.querySelectorAll('.game-chooser button')).forEach(btn => {
    btn.addEventListener('click', () => {
        if (gameManagement[btn.getAttribute('game')]) {
            chooseGame(gameManagement[btn.getAttribute('game')])
        } else {
            console.warn("Unknown game")
        }
    })
})