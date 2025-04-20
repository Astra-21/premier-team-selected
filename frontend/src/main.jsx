import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'; // Tailwind有効化に必須


ReactDOM.createRoot(document.getElementById('root')).render( //domNode を「Reactが支配する場所」に指定する。
  //render ノード内に仮想DOMを反映する。


  <React.StrictMode>
    <App />
  </React.StrictMode>
)

