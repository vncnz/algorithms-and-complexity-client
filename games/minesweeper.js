let bgMine = 'hsl(0, 80%, 50%)'
let bgFlag = 'hsl(0, 80%, 80%)'
let bgGray = "hsl(0, 0%, 80%)"
let bgGreen = "hsl(100, 80%, 80%)"

export const createDefinitionForMinesweeperGame = (preferredSize) => {
    const sz = 12
    const unit = preferredSize / sz

    let mines = []
    let num_mines = Math.ceil(sz * sz / 8)
    let sec = sz * sz // security
    while (mines.length < num_mines && --sec > 0) {
        let rand = `id${parseInt(Math.random() * sz * sz)}`
        if (!mines.includes(rand)) mines.push(rand)
    }
    let game = {
        field: {
            // xsize: sz,
            // ysize: sz,
            width: preferredSize,
            height: preferredSize
        },
        playStatus: {
            status: 'running',
            progression: 0,
            internalData: { mines }
        },
        objects: {},
        events: {}
    }

    for(let i = 0; i < sz; i++) {
        for(let j = 0; j < sz; j++) {
            let id = `id${j*sz + i}`
            // let b = game.playStatus.internalData.mines.includes(id)
            game.objects[id] = {
                id,
                rect: { x: i, y: j, w: 1, h: 1 },
                internalData: { status: 'untouched', mine: mines.includes(id) },
                points: [[i*unit, j*unit], [i*unit + unit, j*unit], [i*unit + unit, j*unit + unit], [i*unit, j*unit + unit]]
            }
            game.events[id] = [ 'click', 'contextmenu' ]
        }
    }
    drawField(game)
    game.playStatus.progression = 1 - (num_mines / Object.values(game.objects).length)
    game.playStatus.progressionText = `${num_mines} left`
    return game
}

export const simulateServerForMinesweeperGame = (objid, evtType, input) => {
    console.warn('Simulating server input', objid, evtType, input)
    let output = JSON.parse(JSON.stringify(input)) // simulo una comunicazione col server quindi non modifico l'oggetto corrente, ovviamente!
    // let objid = objs[0]
    let obj = output.objects[objid]

    let isLeftClick = evtType === 'contextmenu'
    if (isLeftClick) {
        console.log('isLeftClick', isLeftClick)
        if (obj.internalData.status == 'flag') obj.internalData.status = 'untouched'
        else obj.internalData.status = 'flag'
    } else {
        obj.internalData.status = 'seen'
        expand(obj, output)
    }

    if (obj.internalData.status == 'seen') {
        if (obj.internalData.mine) {
            output.playStatus.status = 'lose'
            // Object.values(output.objects).forEach(o => o.events = [])
            output.events[objid] = []
        }
    }

    if (output.playStatus.status == 'lose') {
        Object.values(output.objects).forEach(obj => {
            obj.internalData.status = 'seen'
        })
    }

    drawField(output)

    output.playStatus.progression = (Object.values(output.objects).filter(o => o.internalData.status !== 'untouched').length / (Object.values(output.objects).length))
    if (output.playStatus.status != 'lose' && output.playStatus.progression === 1) {
        output.playStatus.status = 'win'
        output.events = []
    }
    let num_mines = Object.values(output.objects).filter(o => o.internalData.mine).length
    let flags = Object.values(output.objects).filter(o => o.internalData.status === 'flag').length
    output.playStatus.progressionText = `${num_mines - flags} left`
    console.warn('Simulating server output', output)
    return output
}

const countMines = (x, y, board) => {
    return Object.values(board.objects).filter(obj => {
        return Math.abs(obj.rect.x - x) < 2 && Math.abs(obj.rect.y - y) < 2 && obj.internalData.mine
    }).length
}

const expand = (obj, board) => {
    let visited = []
    let frontier = [obj]
    while (frontier.length > 0) {
        obj = frontier.pop()
        visited[obj.id] = true
        let x = obj.rect.x
        let y = obj.rect.y
        if (countMines(x, y, board) === 0) {
            Object.values(board.objects).forEach(obj => {
                if (Math.abs(obj.rect.x - x) < 2 && Math.abs(obj.rect.y - y) < 2 && !obj.internalData.mine && obj.internalData.status == 'untouched') {
                    obj.internalData.status = 'seen'
                    if (!visited[obj.id] && countMines(obj.rect.x, obj.rect.y, board) === 0) {
                        frontier.push(obj)
                    }
                }
            })
        }
    }
}

const drawField = (output) => {
    Object.values(output.objects).forEach(obj => {
        switch (obj.internalData.status) {
            case 'flag':
                obj.text = '🏴'
                obj.bgColor = bgFlag
                break
            case 'seen':
                if (obj.internalData.mine) {
                    obj.text = '💣'
                    obj.bgColor = bgMine
                } else {
                    let c = countMines(obj.rect.x, obj.rect.y, output)
                    obj.text = `${c}`
                    obj.bgColor = bgGreen
                }
                break
            default:
                obj.text = ''
                obj.bgColor = bgGray
        }
    })
}