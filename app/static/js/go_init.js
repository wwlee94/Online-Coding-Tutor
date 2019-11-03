//go.js 기본 설정
function init() {

  // 노드 디자인 + 기능
  myDiagram.nodeTemplate =
    $$(go.Node, "Auto", // the Shape will go around the TextBlock
      {
        click: function(e, node) {
          showConnections(node);
        } // defined below
        // fromSpot: go.Spot.RightSide,
        // toSpot: go.Spot.LeftSide,
      },
      $$(go.Shape, "RoundedRectangle", {
          fill: "black", // the default fill, if there is no data bound value
          //                   portId: "", cursor: "pointer", // the Shape is the port, not the whole Node
          // allow all kinds of links from and to this port
          //                   fromLinkable: true,
          //                   toLinkable: true
        },
        new go.Binding("stroke", "stroke"),
        // Shape.fill is bound to Node.data.color
        new go.Binding("fill", "color")),
      $$(go.TextBlock, {
          font: "bold 14px sans-serif",
          stroke: 'black',
          margin: 5, // make some extra space for the shape around the text
          isMultiline: false, // don't allow newlines in text
          // TextBlock.text is bound to Node.data.key
        },
        new go.Binding("stroke", "text_stroke"),
        new go.Binding("text", "text"))
    );

  //링크 디자인 + 기능
  myDiagram.linkTemplate =
    $$(go.Link, {
        // routing: go.Link.Orthogonal,
        // routing: go.Link.AvoidsNodes,
        curve: go.Link.Bezier,
        fromSpot: go.Spot.RightSide,
        toSpot: go.Spot.AllSides,
        corner: 40
        //                 curve: go.Link.Bezier
      }, // allow the user to relink existing links
      $$(go.Shape, {
          isPanelMain: true,
          stroke: "black",
          strokeWidth: 1.5
        },
        new go.Binding("stroke", "color")),
      // Link.isHighlighted is true 이면 "stroke"를 "red"로 변경
      // new go.Binding("stroke", "isHighlighted", function(h) {
      //   return h ? "red" : "black";
      // }).ofObject()),
      $$(go.Shape, {
          toArrow: "standard",
          stroke: null,
          strokeWidth: 0
        },
        new go.Binding("fill", "color"))
      // Link.isHighlighted is true 이면 "fill"을 "red"로 변경
      // new go.Binding("fill", "isHighlighted", function(h) {
      //   return h ? "red" : "black";
      // }).ofObject())
    );

  // 전역 변수 template
  var globalGroupTemplate =
    $$(go.Group, "Vertical", {
        avoidable: false,
        layerName: "Background"
      },
      $$(go.GridLayout, {
        wrappingColumn: 1,
        // cellSize: new go.Size(1, 1),
        spacing: new go.Size(5, 5)
      }),
      $$(go.TextBlock, {
          font: "bold 15px sans-serif",
          alignment: go.Spot.Left,
          isMultiline: false // don't allow newlines in text
        },
        new go.Binding("text", "text").makeTwoWay(),
        new go.Binding("stroke", "text_color")),
      $$(go.Panel, "Auto", {
          name: "PANEL",
          // margin: new go.Margin(0, 0, 0, 0),
        },
        $$(go.Shape, "RoundedRectangle", // the rectangular shape around the members
          {
            fill: "rgba(128,128,128, 0.4)",
            // fill: "rgba(128,128,128,0.2)" // fill: "rgba(128,128,64,0.2)", "rgba(43,43,43,0.2)"
            stroke: "black", //다른 테마 stroke="black", width:2
            strokeWidth: 2,
            //                         portId: "", cursor: "pointer",  // the Shape is the port, not the whole Node
          },
          new go.Binding("stroke", "color")),
        $$(go.Placeholder, {
          margin: 8,
          background: "transparent"
        }) // represents where the members are
      )
    );

  // Object 틀(panel) template
  var objectPanelGroupTemplate =
    $$(go.Group, "Vertical", {
        avoidable: false,
        layerName: "Background"
      },
      $$(go.GridLayout, {
        alignment: go.GridLayout.Center,
        // 아래 설정 -> 가로로만 나열하는 layout
        // wrappingWidth : Infinity,
        // wrappingColumn : Infinity,
        cellSize: new go.Size(1, 1),
        spacing: new go.Size(5, 5)
      }),
      // new go.Binding("wrappingColumn", "column")),
      $$(go.TextBlock, {
          font: "bold 12px sans-serif",
          alignment: go.Spot.Left,
        },
        new go.Binding("text", "text").makeTwoWay(),
        new go.Binding("stroke", "color")),
      $$(go.Panel, "Auto", {
          name: "PANEL",
        },
        $$(go.Shape, "RoundedRectangle", // the rectangular shape around the members
          {
            fill: "rgba(128,128,128, 0.1)",
            strokeWidth: 0
          }),
        $$(go.Placeholder, {
          margin: 8,
          background: "transparent"
        }) // represents where the members are
      )
    );

  // 생성된 객체 template
  var objectGroupTemplate =
    $$(go.Group, "Vertical", {
        avoidable: false,
        layerName: "Background"
      },
      $$(go.GridLayout, {
        alignment: go.GridLayout.Center,
        //                         wrappingColumn: Infinity,
        cellSize: new go.Size(1, 1),
        spacing: new go.Size(5, 5)
      }),
      $$(go.TextBlock, {
          font: "bold 12px sans-serif",
          alignment: go.Spot.Left,
        },
        new go.Binding("text", "text").makeTwoWay(),
        new go.Binding("stroke", "color")),
      $$(go.Panel, "Auto", {
          name: "PANEL",
        },
        $$(go.Shape, "RoundedRectangle", // the rectangular shape around the members
          {
            fill: "rgba(128,128,128, 0.4)",
            stroke: "black",
            strokeWidth: 2,
            //                         portId: "", cursor: "pointer",  // the Shape is the port, not the whole Node
          },
          new go.Binding("stroke", "isHighlighted", function(h) {
            return h ? "red" : "black";
          }).ofObject()),
        $$(go.Placeholder, {
          margin: 8,
          background: "transparent"
        }) // represents where the members are
      )
    );

  // DICT 타입 template
  var dictGroupTemplate =
    $$(go.Group, "Vertical", {
        avoidable: false,
        layerName: "Background"
      },
      $$(go.GridLayout, {
        alignment: go.GridLayout.Center,
        wrappingColumn: 1,
        cellSize: new go.Size(1, 1),
        spacing: new go.Size(1, 5)
      }),
      $$(go.TextBlock, {
          font: "bold 12px sans-serif",
          alignment: go.Spot.Left,
        },
        new go.Binding("text", "text").makeTwoWay(),
        new go.Binding("stroke", "color")),
      $$(go.Panel, "Auto", {
          name: "PANEL",
        },
        $$(go.Shape, "RoundedRectangle", // the rectangular shape around the members
          {
            fill: "rgba(128,128,128, 0.4)",
            stroke: "black",
            strokeWidth: 2,
            // //                         portId: "", cursor: "pointer",  // the Shape is the port, not the whole Node
          },
          new go.Binding("stroke", "isHighlighted", function(h) {
            return h ? "red" : "black";
          }).ofObject()),
        $$(go.Placeholder, {
          margin: 7,
          background: "transparent"
        }) // represents where the members are
      )
    );

  // DICT 타입 sub틀 template
  var subdictGroupTemplate =
    $$(go.Group, "Vertical", {
        avoidable: false,
        layerName: "Background"
      },
      $$(go.GridLayout, {
        alignment: go.GridLayout.Center,
        //                         wrappingColumn: Infinity,
        cellSize: new go.Size(1, 1),
        spacing: new go.Size(0, 0)
      }),
      $$(go.Panel, "Auto", {
          name: "PANEL",
        },
        $$(go.Shape, "RoundedRectangle", // the rectangular shape around the members
          {
            fill: "rgba(128,128,128, 0)",
            strokeWidth: 0
          }),
        $$(go.Placeholder, {
          margin: 1,
          background: "transparent"
        }) // represents where the members are
      )
    );

  //템플릿 맵 설정
  var templmap = new go.Map();

  templmap.add("", globalGroupTemplate);
  templmap.add("object_panel", objectPanelGroupTemplate);
  templmap.add("object", objectGroupTemplate);
  templmap.add("dict", dictGroupTemplate);
  templmap.add("subdict", subdictGroupTemplate);
  // for the default category, "", use the same template that Diagrams use by default;

  myDiagram.groupTemplateMap = templmap;
}

// 클릭한 노드의 연결된 모든 노드,링크 하이라이트 설정
function showConnections(node) {
  var diagram = node.diagram;
  diagram.startTransaction("highlight");
  // 모든 하이라이트 제거하고
  diagram.clearHighlighteds();
  // 나가는 모든 링크 하이라이트
  node.findLinksOutOf().each(function(l) {
    l.isHighlighted = true;
  });
  // 나가는 모든 노드 하이라이트
  node.findNodesOutOf().each(function(n) {
    n.isHighlighted = true;
  });
  diagram.commitTransaction("highlight");
}

// function CascadeLayout() {
//   go.Layout.call(this);
//   this._offset = new go.Size(12, 12);
// }
// go.Diagram.inherit(CascadeLayout, go.Layout);
//
// CascadeLayout.prototype.cloneProtected = function(copy) {
//   go.Layout.prototype.cloneProtected.call(this, copy);
//   copy._offset = this._offset;
// };
//
// Object.defineProperty(CascadeLayout.prototype, "offset", {
//   get: function() {
//     return this._offset;
//   },
//   set: function(val) {
//     if (!(val instanceof go.Size)) {
//       throw new Error("new value for CascadeLayout.offset must be a Size, not: " + val);
//     }
//     if (!this._offset.equals(val)) {
//       this._offset = val;
//       this.invalidateLayout();
//     }
//   }
// });
//
// /**
//  * This method positions all Nodes and ignores all Links.
//  * @this {CascadeLayout}
//  * @param {Diagram|Group|Iterable} coll the collection of Parts to layout.
//  */
// CascadeLayout.prototype.doLayout = function(coll) {
//   // get the Nodes and Links to be laid out
//   var parts = this.collectParts(coll);
//
//   // Start the layout at the arrangement origin, a property inherited from Layout
//   var x = this.arrangementOrigin.x;
//   var y = this.arrangementOrigin.y;
//   var offset = this.offset;
//
//   var it = parts.iterator;
//   while (it.next()) {
//     var node = it.value;
//     if (!(node instanceof go.Node)) continue; // ignore Links
//     // console.log(node);
//     // // height = node['actualBounds']['height'];
//     // // width = node['actualBounds']['width'];
//
//     // console.log(node.actualbounds);
//     node.move(new go.Point(x, y));
//     x += offset.width;
//     y += offset.height;
//   }
// };
// // end of CascadeLayout
