/* const game = {
    field: {
        xsize: 10,
        ysize: 10
    },
    objects: [{
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
    }]
} */

import { createDefinitionForFlipGame, simulateServerForFlipGame } from '/games/flip.js'

const gameManagement = {
    flip: {
        createDefinition: createDefinitionForFlipGame,
        simulateServer: simulateServerForFlipGame
    }
}
const g = gameManagement.flip

let game = g.createDefinition()

let xpx = 0
let ypx = 0

let draw = () => {
    const canvas = document.querySelector('canvas')
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    ctx.font = "20px Arial";

    const rect = canvas.getBoundingClientRect()
    xpx = rect.width / game.field.xsize
    ypx = rect.height / game.field.xsize

    game.objects.forEach(obj => {
        ctx.fillStyle = obj.bgColor;
        const fromx = xpx * obj.rect.x
        const sizex = xpx * obj.rect.w
        const fromy = ypx * obj.rect.y
        const sizey = ypx * obj.rect.h

        if (obj.bgColor) {
            ctx.fillRect(fromx, fromy, sizex, sizey)
            // console.log(`Drawing rect ${fromx}, ${fromy}, ${sizex}, ${sizey}`)
        }

        if (obj.text) {
            ctx.fillStyle = obj.fgColor;
            const tx = fromx + sizex/2
            const ty = fromy + sizey/2
            let w = ctx.measureText(obj.text).width
            ctx.fillText(obj.text, tx - w/2, ty + w/2)
            // console.log(`Writing text "${obj.text}" at ${tx}, ${ty}`)
        }
    })

    document.querySelector('#game-status').innerHTML = `${game.info.status} (${Math.round(game.info.progression * 100)}%)`
    // ctx.fillStyle = "rgb(200 0 0)";
    // ctx.fillRect(10, 10, 50, 50);

    // ctx.fillStyle = "rgb(0 0 200 / 50%)";
    // ctx.fillRect(30, 30, 50, 50);
}
draw()

const cellAt = (x, y) => {
    return {
        x: Math.floor(x / xpx),
        y: Math.floor(y / ypx)
    }
}

const objectsAt = (x, y) => {
    const cell = cellAt(x, y)
    const collisions = game.objects.filter(obj =>
        cell.x >= obj.rect.x &&
        cell.x < obj.rect.x + obj.rect.w &&
        cell.y >= obj.rect.y &&
        cell.y < obj.rect.y + obj.rect.h
    )
    return collisions
}

let bindEvents = () => {
    const canvas = document.querySelector('canvas')
    if (!canvas) return

    let canvasRect = canvas.getBoundingClientRect()

    canvas.addEventListener('click', evt => {
        console.log('click', evt)
        const x = evt.pageX - canvasRect.left
        const y = evt.pageY - canvasRect.top
        console.log(x, y)
        // const coo = cellAt(x, y)
        const objs = objectsAt(x, y)
        const withEvent = objs.filter(obj => (obj.events || []).includes('click'))
        console.log(objs, withEvent)
        game = g.simulateServer(objs.map(o => o.id), 'click', game)
        draw()
    })
}
bindEvents()