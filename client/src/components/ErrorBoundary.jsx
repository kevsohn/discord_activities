import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error("Renderer crashed:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 text-center text-red-500">
          <h2 className="text-lg font-bold">Something went wrong</h2>
          <pre className="text-xs opacity-70">
            {this.state.error?.message}
          </pre>
        </div>
      );
    }

    return this.props.children;
  }
}

