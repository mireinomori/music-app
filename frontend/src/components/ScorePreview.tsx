import {useEffect,useRef,useState} from 'react';

export default function ScorePreview({xmlUrl}:{xmlUrl:string}){
  const ref=useRef<HTMLDivElement>(null);
  const[error,setError]=useState<string|null>(null);
  useEffect(()=>{
    let live=true;
    const render=async()=>{
      try{
        if(xmlUrl.includes('/api/demo-score')){
          setError('音声ファイルを解析すると、生成した楽譜がここに表示されます。');
          return;
        }
        const{OpenSheetMusicDisplay}=await import('opensheetmusicdisplay');
        const res=await fetch(xmlUrl);
        if(!res.ok)throw new Error(`MusicXML取得失敗: ${res.status}`);
        const xml=await res.text();
        if(!live||!ref.current)return;
        ref.current.innerHTML='';
        const osmd=new OpenSheetMusicDisplay(ref.current,{autoResize:true,drawTitle:true});
        await osmd.load(xml);
        osmd.render();
      }catch{if(live)setError('生成したMusicXMLを読み込めませんでした。もう一度解析してください。');}
    };
    setError(null); render();
    return()=>{live=false};
  },[xmlUrl]);
  return <div className="score-paper">{error?<p className="score-fallback">{error}</p>:<div ref={ref} className="osmd"/>}</div>;
}
