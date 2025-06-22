export const createDefinitionForFlipGame = (preferredSize) => {
    let sz = 4
    const unit = preferredSize / sz
    let game = {
        field: {
            xsize: sz,
            ysize: sz
        },
        playStatus: {
            status: 'running',
            progression: 0
        },
        objects: {},
        events: {}
    }
    for(let i = 0; i < sz; i++) {
        for(let j = 0; j < sz; j++) {
            let b = Math.random() > .5
            let id = j*sz + i
            game.objects[id] = {
                id,
                rect: { x: i, y: j },
                internalData: { on: b },
                points: [[i*unit, j*unit], [i*unit + unit, j*unit], [i*unit + unit, j*unit + unit], [i*unit, j*unit + unit]]
            }
            game.events[id] = [ 'click' ]
        }
    }
    drawField(game)
    game.playStatus.progression = Object.values(game.objects).filter(o => o.internalData.on).length / Object.values(game.objects).length
    return game
}


export const simulateServerForFlipGame = (objid, evtType, input) => {
    console.warn('Simulating server', objid, evtType, input)
    let output = JSON.parse(JSON.stringify(input)) // simulo una comunicazione col server quindi non modifico l'oggetto corrente, ovviamente!
    let obj = output.objects[objid]
    Object.values(output.objects).forEach(o => {
        let xdiff = Math.abs(obj.rect.x - o.rect.x)
        let ydiff = Math.abs(obj.rect.y - o.rect.y)

        if ((xdiff == 0 && Math.abs(ydiff) < 2) ||
            (ydiff == 0 && Math.abs(xdiff) < 2)) {
            o.internalData.on = !o.internalData.on
        }
    })
    drawField(output)
    output.playStatus.progression = Object.values(output.objects).filter(o => o.internalData.on).length / Object.values(output.objects).length
    if (output.playStatus.progression === 1) {
        output.playStatus.status = 'win'
        output.events = {}
    }
    return output
}

const drawField = (output) => {
    let lightUp = 'hsl(0, 0%, 80%)'
    let lightDown = "hsl(0, 0%, 20%)"
    Object.values(output.objects).forEach(obj => {
        if (obj.internalData.on) {
            obj.text = '💡'
            obj.bgColor = lightUp
        } else {
            obj.text = '🕯️'
            obj.bgColor = lightDown
        }
    })
}