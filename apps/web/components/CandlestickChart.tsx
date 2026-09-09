"use client";

type Candle={timestamp:string;open:string|number;high:string|number;low:string|number;close:string|number};
type Event={event:string;timestamp:string;price:string|number};

export default function CandlestickChart({candles,events}:{candles:Candle[];events:Event[]}){
 if(!candles.length)return <div className="muted">No candles returned for this range.</div>;
 const w=900,h=390,p=36, highs=candles.map(c=>Number(c.high)), lows=candles.map(c=>Number(c.low));
 const max=Math.max(...highs),min=Math.min(...lows),range=max-min||1;
 const x=(i:number)=>p+i*((w-2*p)/Math.max(candles.length-1,1));
 const y=(v:number)=>h-p-(v-min)/range*(h-2*p);
 const eventByTime=new Map(events.map(e=>[new Date(e.timestamp).getTime(),e]));
 return <svg className="chart" viewBox={`0 0 ${w} ${h}`} width="100%" role="img" aria-label="NIFTY candlestick chart">
  {[0,0.25,0.5,0.75,1].map(t=><g key={t}><line x1={p} x2={w-p} y1={y(min+range*t)} y2={y(min+range*t)} stroke="#26314a"/><text className="axis" x={4} y={y(min+range*t)+4}>{(min+range*t).toFixed(2)}</text></g>)}
  {candles.map((c,i)=>{const o=Number(c.open),cl=Number(c.close),hi=Number(c.high),lo=Number(c.low),up=cl>=o,cx=x(i),bw=Math.max(2,Math.min(9,(w-2*p)/candles.length*.65)),e=eventByTime.get(new Date(c.timestamp).getTime());return <g key={c.timestamp}><line x1={cx} x2={cx} y1={y(hi)} y2={y(lo)} stroke={up?"#5ee6a8":"#ff7d8a"}/><rect x={cx-bw/2} y={y(Math.max(o,cl))} width={bw} height={Math.max(1,Math.abs(y(o)-y(cl)))} fill={up?"#5ee6a8":"#ff7d8a"}/>{e&&<circle cx={cx} cy={y(Number(e.price))} r="4" fill="#ffd166"/>}</g>})}
 </svg>;
}
