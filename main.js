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

const gameManagement = {
    flip: {
        createDefinition: createDefinitionForFlipGame,
        simulateServer: simulateServerForFlipGame
    },
    minesweeper: {
        createDefinition: createDefinitionForMinesweeperGame,
        simulateServer: simulateServerForMinesweeperGame
    }
}
const g = gameManagement.minesweeper

let game = g.createDefinition()

let xpx = 0
let ypx = 0

let createSvgChild = (type, attrs, content) => {
    let elm = document.createElementNS('http://www.w3.org/2000/svg', type)
    for (const [key, value] of Object.entries(attrs)) {
        elm.setAttribute(key, value)
    }
    if (content) elm.innerHTML = content
    return elm
}
let draw = () => {
    const svg = document.querySelector('svg')
    if (!svg) return
    // ctx.font = "20px Arial";
    svg.innerHTML = ""

    const rect = svg.getBoundingClientRect()
    xpx = rect.width / game.field.xsize
    ypx = rect.height / game.field.xsize

    svg.setAttribute("viewBox", `0 0 ${rect.width} ${rect.height}`)

    Object.values(game.objects).forEach(obj => {
        // ctx.fillStyle = obj.bgColor;
        const fromx = xpx * obj.rect.x
        const sizex = xpx * obj.rect.w
        const fromy = ypx * obj.rect.y
        const sizey = ypx * obj.rect.h
        console.log(fromx, fromy, sizex, sizey)

        let rect = createSvgChild('rect', {
            x: fromx,
            y: fromy,
            width: sizex,
            height: sizey,
            id: obj.id,
            fill: obj.bgColor || "transparent",
            stroke: 'gray'
        })
        svg.appendChild(rect)

        if (obj.text) {
            //ctx.fillStyle = obj.fgColor;
            const tx = fromx + sizex/2
            const ty = fromy + sizey/2
            let text = createSvgChild('text', {
                x: tx,
                y: ty,
                style: 'pointer-events: none'
            }, obj.text)
            svg.appendChild(text)
            // let w = ctx.measureText(obj.text).width
            //ctx.fillText(obj.text, tx - w/2, ty + w/2)
        }
    })

    document.querySelector('#game-status').innerHTML = `${game.playStatus.status} (${Math.round(game.playStatus.progression * 100)}%)`
    // ctx.fillStyle = "rgb(200 0 0)";
    // ctx.fillRect(10, 10, 50, 50);

    // ctx.fillStyle = "rgb(0 0 200 / 50%)";
    // ctx.fillRect(30, 30, 50, 50);
}
draw()

let bindEvents = () => {
    for (const [key, value] of Object.entries(game.events)) {
        let elm = document.getElementById(key)
        if (elm) {
            value.forEach(evtType => {
                elm.addEventListener(evtType, evt => {
                    evt.preventDefault()
                    game = g.simulateServer(key, evtType, game)
                    draw()
                    bindEvents()
                })
            })
        }
    }
}
bindEvents()