import {useEffect,useRef,useState} from 'react';

export default function ScorePreview({xmlUrl}:{xmlUrl:string}){
  const ref=useRef<HTMLDivElement>(null);
  const[error,setError]=useState<string|null>(null);
  const[lyricsState,setLyricsState]=useState<'idle'|'working'|'done'>('idle');
  const[lyricsMessage,setLyricsMessage]=useState('');
  const[refresh,setRefresh]=useState(0);
  const isJob=xmlUrl.includes('/api/jobs/');
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
        await osmd.load(xml); osmd.render();
      }catch{if(live)setError('生成したMusicXMLを読み込めませんでした。もう一度解析してください。');}
    };
    setError(null); render();
    return()=>{live=false};
  },[xmlUrl,refresh]);
  const recognizeLyrics=async()=>{
    setLyricsState('working'); setLyricsMessage('歌詞を認識しています…');
    try{
      const url=xmlUrl.replace(/\/musicxml$/, '/lyrics');
      const res=await fetch(url,{method:'POST'}); const data=await res.json();
      if(!res.ok)throw new Error(data.detail??'歌詞認識に失敗しました。');
      setLyricsState('done'); setLyricsMessage(`歌詞を${data.word_count}語認識しました。`); setRefresh(value=>value+1);
    }catch(error){setLyricsState('idle');setLyricsMessage(error instanceof Error?error.message:'歌詞認識に失敗しました。');}
  };
  return <>
    <div className="score-paper">{error?<p className="score-fallback">{error}</p>:<div ref={ref} className="osmd"/>}</div>
    {isJob&&<div className="lyrics-tools"><button onClick={recognizeLyrics} disabled={lyricsState==='working'}>{lyricsState==='working'?'歌詞を認識中…':'歌詞を自動認識'}</button>{lyricsMessage&&<span>{lyricsMessage}</span>}</div>}
  </>;
}
