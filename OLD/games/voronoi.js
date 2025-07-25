export class VoronoiDiagram {
	/**
	 * Creates an instance of the Voronoi diagram builder
	 * @param {[Point]} points - List of Points objects p having x and y coordinate p.x and p.y
	 * @param {float} width - Width of the canvas
	 * @param {float} height - Height of the canvas
	 */
	constructor(points, width, height) {
		this.point_list = points;
		this.reset();
		this.box_x = width;
		this.box_y = height;
	}

	reset() {
		this.event_list = new SortedQueue();
		this.beachline_root = null;
		this.voronoi_vertex = [];
		this.edges = [];
	}

	/**
	 * Builds the Voronoi diagram computing the Voroni vertices and edges
	 */
	update() {
		this.reset();
		let points = [];
		let e = null;
		for (const p of this.point_list) points.push(new Event("point", p));
		this.event_list.points = points;

		while (this.event_list.length > 0) {
			e = this.event_list.extract_first();
			if (e.type == "point") this.point_event(e.position);
			else if (e.active) this.circle_event(e);
			// last_event = e.position;
		}
		this.complete_segments(e.position);
	}

	/**
	 * Handles the Point Events
	 * @param {Point} p - a point object that must have coordinates p.x and p.y
	 */
	point_event(p) {
		let q = this.beachline_root;
		if (q == null) this.beachline_root = new Arc(null, null, p, null, null);
		else {
			while (
				q.right != null &&
				this.parabola_intersection(p.y, q.focus, q.right.focus) <= p.x
			) {
				q = q.right;
			}

			// if(q === this.beachline_root && q.focus.y == p.y) xx = (q.focus.x + p.x)/2 // edge case when the two top sites have same y
			let e_qp = new Edge(q.focus, p, p.x);
			let e_pq = new Edge(p, q.focus, p.x);

			let arc_p = new Arc(q, null, p, e_qp, e_pq);
			let arc_qr = new Arc(arc_p, q.right, q.focus, e_pq, q.edge.right);
			if (q.right) q.right.left = arc_qr;
			arc_p.right = arc_qr;
			q.right = arc_p;
			q.edge.right = e_qp;

			// Disable old event
			if (q.event) q.event.active = false;

			// Check edges intersection
			this.add_circle_event(p, q);
			this.add_circle_event(p, arc_qr);

			this.edges.push(e_qp);
			this.edges.push(e_pq);
		}
	}

	/**
	 * Handles the circle event
	 * @param {Event} e - Event type object
	 */
	circle_event(e) {
		let arc = e.caller;
		let p = e.position;
		let edge_new = new Edge(arc.left.focus, arc.right.focus);

		// Disable events
		if (arc.left.event) arc.left.event.active = false;
		if (arc.right.event) arc.right.event.active = false;

		// Adjust beachline deleting the shrinking arc
		arc.left.edge.right = edge_new;
		arc.right.edge.left = edge_new;
		arc.left.right = arc.right;
		arc.right.left = arc.left;

		this.edges.push(edge_new);

		if (!this.point_outside(e.vertex)) this.voronoi_vertex.push(e.vertex); // Only add the vertex if inside canvas
		arc.edge.left.end = arc.edge.right.end = edge_new.start = e.vertex; // This needs to come before add_circle_event as it is used there

		this.add_circle_event(p, arc.left);
		this.add_circle_event(p, arc.right);
	}

	/**
	 * Tests if the arc event is valid and adds it into the queue
	 * @param {Point} p - Current position of the sweepline
	 * @param {Arc} arc - The Arc tested
	 */
	add_circle_event(p, arc) {
		if (arc.left && arc.right) {
			let a = arc.left.focus;
			let b = arc.focus;
			let c = arc.right.focus;

			//Compute sine of angle between focuses. if positive then edges intersect
			if ((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y) > 0) {
				let new_inters = this.edge_intersection(
					arc.edge.left,
					arc.edge.right
				);
				let circle_radius = Math.sqrt(
					(new_inters.x - arc.focus.x) ** 2 +
						(new_inters.y - arc.focus.y) ** 2
				);
				let event_pos = circle_radius + new_inters.y;
				if (event_pos > p.y && new_inters.y < this.box_y) {
					// This is important new_inters.y < this.box_y
					let e = new Event(
						"circle",
						new Point(new_inters.x, event_pos),
						arc,
						new_inters
					);
					arc.event = e;
					this.event_list.insert(e);
				}
			}
		}
	}

	// Input: float, Point, Point
	/**
	 * Computes the intersection of two parabolas given the directrix
	 * @param {float} y - position of the directrix (sweepline)
	 * @param {Point} f1 - Focus of first parabola
	 * @param {Point} f2 - Focus of second parabola
	 * @returns	{float} Intersection x-coordinate
	 */
	parabola_intersection(y, f1, f2) {
		let fyDiff = f1.y - f2.y;
		if (fyDiff == 0) return (f1.x + f2.x) / 2;
		let fxDiff = f1.x - f2.x;
		let b1md = f1.y - y; //Difference btw parabola 1 fy and directrix
		let b2md = f2.y - y; //Difference btw parabola 2 fy and directrix
		let h1 = (-f1.x * b2md + f2.x * b1md) / fyDiff;
		let h2 = Math.sqrt(b1md * b2md * (fxDiff ** 2 + fyDiff ** 2)) / fyDiff;

		return h1 + h2; //Returning the left x coord of intersection. Remember top of canvas is 0 hence parabolas are facing down
	}

	/**
	 * Computes the intersection point of two edges
	 * @param {Edge} e1 - First edge
	 * @param {Edge} e2 - Second edge
	 * @returns {Point} Intersection point
	 */
	edge_intersection(e1, e2) {
		if (e1.m == Infinity) return new Point(e1.start.x, e2.getY(e1.start.x));
		else if (e2.m == Infinity)
			return new Point(e2.start.x, e1.getY(e2.start.x));
		else {
			let mdif = e1.m - e2.m;
			if (mdif == 0) return null;
			let x = (e2.q - e1.q) / mdif;
			let y = e1.getY(x);
			return new Point(x, y);
		}
	}

	/**
	 * Completes the Voronoi edges taking into account the canvas sizes
	 * @param {Point} last - last point extracted from the queue
	 */
	complete_segments(last) {
		let r = this.beachline_root;
		let e, x, y;
		// Complete edges attached to beachline
		while (r.right) {
			e = r.edge.right;
			x = this.parabola_intersection(
				last.y * 1.1,
				e.arc.left,
				e.arc.right
			); // Check parabola intersection assuming sweepline position equal to last event increased by 10%
			y = e.getY(x);

			// Find end point
			if (
				(e.start.y < 0 && y < e.start.y) ||
				(e.start.x < 0 && x < e.start.x) ||
				(e.start.x > this.box_x && x > e.start.x)
			) {
				e.end = e.start; //If invalid make start = end so it will be deleted later
			} else {
				// If slope has same sign of the difference between start point x coord
				// and parabola intersection then will intersect the top border (y = 0)
				if (e.m == 0) {
					x - e.start.x <= 0 ? (x = 0) : (x = this.box_x);
					e.end = new Point(x, e.start.y);
					this.voronoi_vertex.push(e.end);
				} else {
					// If edge is vertical and is connected to the beachline will end on the bottom border
					if (e.m == Infinity) y = this.box_y;
					else
						e.m * (x - e.start.x) <= 0 ? (y = 0) : (y = this.box_y);
					e.end = this.edge_end(e, y);
				}
			}
			r = r.right;
		}

		let option;

		for (let i = 0; i < this.edges.length; i++) {
			e = this.edges[i];
			option =
				1 * this.point_outside(e.start) + 2 * this.point_outside(e.end);

			switch (option) {
				case 3: // Both endpoints outside the canvas
					this.edges[i] = null;
					break;
				case 1: // Start is outside
					e.start.y < e.end.y ? (y = 0) : (y = this.box_y);
					e.start = this.edge_end(e, y);
					break;
				case 2: // End is outside
					e.end.y <= e.start.y ? (y = 0) : (y = this.box_y);

					e.end = this.edge_end(e, y);
					break;
				default:
					break;
			}
		}
	}

	/**
	 * Computes the intersection point between an edge and the canvas bounding box
	 * @param {Edge} e - Edge being completed
	 * @param {float} y_lim - Either 0 or y limit of the canvas
	 */
	edge_end(e, y_lim) {
		let x = Math.min(this.box_x, Math.max(0, e.getX(y_lim)));
		let y = e.getY(x);
		if (!y) y = y_lim; // In this case the edge is vertical
		let p = new Point(x, y);
		this.voronoi_vertex.push(p);
		return p;
	}

	/**
	 * Tests if a point is outside the canvas bounding box
	 * @param {Point} p - Point tested
	 */
	point_outside(p) {
		return p.x < 0 || p.x > this.box_x || p.y < 0 || p.y > this.box_y;
	}
}

class Arc {
	constructor(l, r, f, el, er) {
		this.left = l;
		this.right = r;
		this.focus = f; // Point
		this.edge = { left: el, right: er }; // Edge
		this.event = null;
	}
}

export class Point {
	constructor(x, y) {
		this.x = x;
		this.y = y;
	}

	toString () { //* non fa l'override, va chiamato manualmente
		return `(${this.x}, ${this.y})`
	}
}

export class Edge {
	constructor(p1, p2, startx) {
		this.m = -(p1.x - p2.x) / (p1.y - p2.y);
		this.q =
			(0.5 * (p1.x ** 2 - p2.x ** 2 + p1.y ** 2 - p2.y ** 2)) /
			(p1.y - p2.y);
		this.arc = { left: p1, right: p2 };
		this.end = null;
		this.start = null;
		if (startx)
			this.start = new Point(
				startx,
				this.m != Infinity ? this.getY(startx) : null
			);
	}
	getY(x) {
		if (this.m == Infinity) return null;
		return x * this.m + this.q;
	}
	getX(y) {
		if (this.m == Infinity) return this.start.x;
		return (y - this.q) / this.m;
	}
}

class Event {
	constructor(type, position, caller, vertex) {
		this.type = type;
		this.caller = caller;
		this.position = position;
		this.vertex = vertex;
		this.active = true;
	}
}

class SortedQueue {
	constructor(events) {
		this.list = [];
		if (events) this.list = events;
		this.sort();
	}

	get length() {
		return this.list.length;
	}

	extract_first() {
		if (this.list.length > 0) {
			let elm = this.list[0];
			this.list.splice(0, 1);
			return elm;
		}
		return null;
	}

	insert(event) {
		this.list.push(event);
		this.sort();
	}

	set points(events) {
		this.list = events;
		this.sort();
	}

	sort() {
		this.list.sort(function (a, b) {
			let diff = a.position.y - b.position.y;
			if (diff == 0) return a.position.x - b.position.x; // If events are at the same height the one on the left should be first
			return diff;
		});
	}
}