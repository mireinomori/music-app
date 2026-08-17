import {useEffect,useRef,useState} from 'react';

export default function ScorePreview({xmlUrl}:{xmlUrl:string}){
  const ref=useRef<HTMLDivElement>(null);
  const[error,setError]=useState<string|null>(null);
  const[lyrics,setLyrics]=useState('');
  const[lyricsMessage,setLyricsMessage]=useState('');
  const[refresh,setRefresh]=useState(0);
  const isJob=xmlUrl.includes('/api/jobs/');
  useEffect(()=>{
    let live=true;
    const render=async()=>{
      try{
        if(xmlUrl.includes('/api/demo-score')){setError('音声ファイルを解析すると、生成した楽譜がここに表示されます。');return;}
        const{OpenSheetMusicDisplay}=await import('opensheetmusicdisplay');
        const res=await fetch(xmlUrl); if(!res.ok)throw new Error();
        const xml=await res.text(); if(!live||!ref.current)return;
        ref.current.innerHTML=''; const osmd=new OpenSheetMusicDisplay(ref.current,{autoResize:true,drawTitle:true});
        await osmd.load(xml); osmd.render();
      }catch{if(live)setError('生成したMusicXMLを読み込めませんでした。もう一度解析してください。');}
    };
    setError(null); render(); return()=>{live=false};
  },[xmlUrl,refresh]);
  const addLyrics=async()=>{
    if(!lyrics.trim()){setLyricsMessage('歌詞を入力してください。');return;}
    const body=new FormData(); body.append('lyrics',lyrics); setLyricsMessage('歌詞を楽譜に追加しています…');
    try{const res=await fetch(xmlUrl.replace(/\/musicxml$/,'/lyrics-text'),{method:'POST',body});const data=await res.json();if(!res.ok)throw new Error(data.detail??'歌詞の追加に失敗しました。');setLyricsMessage(`歌詞を${data.word_count}文字追加しました。`);setRefresh(value=>value+1);}
    catch(error){setLyricsMessage(error instanceof Error?error.message:'歌詞の追加に失敗しました。');}
  };
  const recognizeLyrics=async()=>{setLyricsMessage('歌詞を認識しています…');try{const res=await fetch(xmlUrl.replace(/\/musicxml$/,'/lyrics'),{method:'POST'});const data=await res.json();if(!res.ok)throw new Error(data.detail??'歌詞認識に失敗しました。');setLyricsMessage(`自動認識した歌詞を${data.word_count}文字追加しました。`);setRefresh(value=>value+1);}catch(error){setLyricsMessage(error instanceof Error?error.message:'歌詞認識に失敗しました。');}};
  return <>
    <div className="score-paper">{error?<p className="score-fallback">{error}</p>:<div ref={ref} className="osmd"/>}</div>
    {isJob&&<div className="lyrics-tools"><textarea value={lyrics} onChange={event=>setLyrics(event.target.value)} placeholder="歌詞を入力してください" rows={3}/><div><button onClick={addLyrics}>歌詞を楽譜に追加</button><button onClick={recognizeLyrics}>自動認識</button><p>{lyricsMessage}</p></div></div>}
  </>;
}
