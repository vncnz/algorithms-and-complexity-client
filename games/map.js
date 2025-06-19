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

    polygons.forEach((poly, idx) => {
        let id = `id${idx}`
        let locked = false
        game.objects[id] = {
            id,
            internalData: { locked, color: Math.floor(Math.random() * colors.length) },
            points: poly.map(point => [point[0]/1000 * preferredSize, point[1]/862 * preferredSize])
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