# Call Graph Visualization Feature

## Overview
The Call Graph Visualization feature provides an interactive graphical representation of function call relationships within your program. It helps users understand the flow of execution and dependencies between functions.

## How to Use
1. **Access the Call Graph**: Navigate to `/call-graph` in your web application.
2. **View the Graph**: The graph displays nodes (functions) and edges (calls between functions).
3. **Interact**: Click on any node to view details about that function below the graph.

## Technical Details
- **Component**: `CallGraph` located at `webapp/src/components/CallGraph/CallGraph.jsx`.
- **Library**: Uses `react-flow-renderer` for graph visualization.
- **Data**: Currently uses static sample data. Can be extended to use real backend data.
- **Styling**: Custom styles in `CallGraph.css`.

## Future Improvements
- Integrate with backend to display real function call data.
- Add search/filter for large graphs.
- Enhance node details with more metadata.

## Example Screenshot
> (Add a screenshot of the call graph UI here)

---
For questions or contributions, see the main project README or contact the maintainers.
