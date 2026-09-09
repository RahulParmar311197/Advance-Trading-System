type EquityPoint = {index:number; timestamp:string; equity:number|string};
type Result={status?:string;data_version?:string;candle_count?:number;signal_count?:number;trade_count?:number;metrics?:Record<string,unknown>;equity_curve?:EquityPoint[];trades?:Array<Record<string,unknown>>};
const show=(v:unknown)=>v===null||v===undefined?"—":typeof v==="number"?v.toFixed(4):String(v);
export default function BacktestResults({result}:{result:Result|null}){
  if(!result)return <div className="muted">Run a backtest to see results.</div>;
  const m=result.metrics||{};
  const curve=result.equity_curve||[];
  const values=curve.map(p=>Number(p.equity)).filter(Number.isFinite);
  const min=Math.min(...values),max=Math.max(...values),range=max-min||1;
  const width=760,height=180;
  const points=curve.map((p,i)=>`${curve.length===1?0:(i/(curve.length-1))*width},${height-((Number(p.equity)-min)/range)*(height-20)-10}`).join(" ");
  return <>
    <div className="metrics">{["total_return","win_rate","profit_factor","expectancy","max_drawdown","average_trade"].map(k=><div className="metric" key={k}><span className="muted">{k.replaceAll("_"," ")}</span><b>{show(m[k])}</b></div>)}</div>
    <p className="muted">{result.trade_count??0} trades · {result.signal_count??0} signals · data {result.data_version}</p>
    {curve.length>0&&<section><h3>Realized equity curve</h3><svg viewBox={`0 0 ${width} ${height}`} className="equity-chart" role="img" aria-label="Realized equity curve"><polyline fill="none" stroke="currentColor" strokeWidth="2" points={points}/></svg><div className="muted">Start {show(curve[0].equity)} · End {show(curve[curve.length-1].equity)}</div></section>}
    {(result.trades||[]).length>0&&<table className="table"><thead><tr><th>Direction</th><th>Entry</th><th>Exit</th><th>Net P&L</th></tr></thead><tbody>{result.trades!.map((t,i)=><tr key={i}><td>{String(t.direction)}</td><td>{show(t.entry)}</td><td>{show(t.exit)}</td><td>{show(t.net_pnl)}</td></tr>)}</tbody></table>}
  </>;
}
