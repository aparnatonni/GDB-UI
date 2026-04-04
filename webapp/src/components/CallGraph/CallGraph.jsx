import React, { useState } from "react";
import ReactFlow, { Background, Controls, MiniMap } from "react-flow-renderer";
import "./CallGraph.css";

const nodes = [
  { id: "1", data: { label: "main" }, position: { x: 100, y: 50 } },
  { id: "2", data: { label: "foo" }, position: { x: 300, y: 0 } },
  { id: "3", data: { label: "bar" }, position: { x: 300, y: 100 } },
  { id: "4", data: { label: "baz" }, position: { x: 500, y: 50 } },
];

const edges = [
  { id: "e1-2", source: "1", target: "2", animated: true },
  { id: "e1-3", source: "1", target: "3", animated: true },
  { id: "e2-4", source: "2", target: "4", animated: true },
  { id: "e3-4", source: "3", target: "4", animated: true },
];

const functionDetails = {
  main: "Entry point of the program.",
  foo: "Performs foo operation.",
  bar: "Handles bar logic.",
  baz: "Finalizes the process.",
};

const CallGraph = () => {
  const [selected, setSelected] = useState(null);

  const onNodeClick = (_event, node) => {
    setSelected(node.data.label);
  };

  return (
    <div className="call-graph-container">
      <h2>Call Graph Visualization</h2>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        style={{ width: "100%", height: 400 }}
        onNodeClick={onNodeClick}
      >
        <MiniMap />
        <Controls />
        <Background gap={16} />
      </ReactFlow>
      {selected && (
        <div style={{ marginTop: 16, padding: 8, background: "#f0f0f0", borderRadius: 4 }}>
          <strong>{selected}</strong>: {functionDetails[selected]}
        </div>
      )}
    </div>
  );
};

export default CallGraph;
