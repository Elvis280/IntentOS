import { useEffect,useState } from 'react'
import api from "./services/api";

function App(){
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);

  const [image,setImage] = useState("");

  useEffect(()=>{
    api.get("/").then(res=> setStatus(res.data)).catch(console.error);
  },[]);

async function analyzeScreen() {
    try{
      const res = await api.post("/vision/analyze");
      setImage(res.data.image);
      setResult(res.data.world)
    }
    catch(err){
      console.error(err);
    }

  }

  return (
    <div style={{padding:"40px"}}>
      <h1>IntentOS</h1>
      <p><strong>Backend Status:</strong> {status?.Status}</p>
      <button onClick={analyzeScreen}>Analyze Screen</button>
      <br />
      <br />
      {result && (
        <div>

          <h2>World State</h2>

          <p>
            <strong>Summary:</strong> {result.summary}
          </p>

          <p>
            <strong>Active Window:</strong> {result.active_window}
          </p>

          <h3>Applications</h3>

          <ul>
            {result.applications?.map(app => (
              <li key={app}>{app}</li>
            ))}
          </ul>

          <h3>Buttons</h3>

          <ul>
            {result.buttons?.map(button => (
              <li key={button}>{button}</li>
            ))}
          </ul>

          <h3>Visible Text</h3>

          <ul>
            {result.text?.map((txt, index) => (
              <li key={index}>{txt}</li>
            ))}
          </ul>

        </div>
      )}
      {image && (<img 
      src={`data:image/png;base64,${image}`} 
      alt="Screenshot" 
      width="800"
      />
      )}
    </div>
  );
}

export default App;