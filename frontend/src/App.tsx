import { useEffect, useMemo, useState } from "react";
import {
  ArrowDownRight,
  ArrowUpRight,
  Minus,
  Moon,
  RefreshCw,
  Sun,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ComposedChart,
  LabelList,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { api } from "./api";


type KPI = {
  title: string;
  actual: number;
  plan: number | null;
  variance: number | null;
  achievement_pct: number | null;
  unit: string;
};

type Row = {
  label: string;
  cells?: number;
  on_date: number;
  mtd: number;
  ytd: number;
};

type Overview = {
  as_of: string;
  kpis: KPI[];
  distribution: Row[];
  rejection: Row[];
  yield_table: Row[];
  rejection_percentage_table: Row[];
};

type Trends = {
  production: any[];
  rejection: any[];
  yield: any[];
  wafer_loss: any[];
  breakage: Record<string, number>;
  breakage_daily?: any[];
  monthly_average: any[];
};


const fmt = (
  value: number | null | undefined,
  decimals = 2,
) =>
  value == null
    ? "N/A"
    : Number(value).toLocaleString(undefined, {
        maximumFractionDigits: decimals,
      });


const percentTick = (value: number) =>
  `${Number(value).toFixed(1)}%`;


const shortDate = (value: string) =>
  new Date(`${value}T00:00:00`).toLocaleDateString(
    "en-GB",
    {
      day: "2-digit",
      month: "short",
    },
  );


const monthLabel = (value: string) =>
  new Date(`${value}T00:00:00`).toLocaleDateString(
    "en-GB",
    {
      month: "short",
      year: "2-digit",
    },
  );


const cellTick = (value: number) => {
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }

  if (value >= 1_000) {
    return `${Math.round(value / 1_000)}k`;
  }

  return `${value}`;
};


const axis = {
  tick: {
    fill: "#43544a",
    fontSize: 11,
    fontWeight: 600,
  },
  tickLine: false,
  axisLine: {
    stroke: "#aebbb3",
  },
};


function KpiCard({ k }: { k: KPI }) {
  const positive =
    k.variance == null
      ? null
      : k.variance >= 0;

  const Icon =
    positive == null
      ? Minus
      : positive
        ? ArrowUpRight
        : ArrowDownRight;

  const label =
    k.title === "Run rate"
      ? "Required"
      : "Plan";

  return (
    <article
      className={`kpi ${
        positive == null
          ? "neutral"
          : positive
            ? "positive"
            : "negative"
      }`}
    >
      <div className="kpiTop">
        <span>{k.title}</span>
        <Icon />
      </div>

      <div className="compare">
        <div>
          <small>Actual</small>
          <strong>{fmt(k.actual)}</strong>
          <em>{k.unit}</em>
        </div>

        <i />

        <div>
          <small>{label}</small>
          <strong>{fmt(k.plan)}</strong>
          <em>{k.unit}</em>
        </div>
      </div>

      <footer>
        <b>
          {k.variance == null
            ? "Comparison unavailable"
            : `${positive ? "+" : ""}${fmt(
                k.variance,
              )} ${k.unit}`}
        </b>

        <span>
          {k.achievement_pct == null
            ? ""
            : `${fmt(
                k.achievement_pct,
              )}% achieved`}
        </span>
      </footer>
    </article>
  );
}


function Chart({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="panel chartPanel">
      <div className="chartHeading">
        <div>
          <h2>{title}</h2>

          {subtitle && (
            <p>{subtitle}</p>
          )}
        </div>
      </div>

      <div className="chart">
        {children}
      </div>
    </section>
  );
}


function TooltipBox({
  active,
  payload,
  label,
}: any) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div className="tooltip">
      <b>
        {label
          ? shortDate(label)
          : ""}
      </b>

      {payload.map((item: any) => {
        const isPercentage =
          String(item.dataKey)
            .toLowerCase()
            .includes("pct") ||
          String(item.name)
            .includes("%");

        return (
          <span
            key={item.dataKey}
            style={{
              color: item.color,
            }}
          >
            {item.name}:{" "}
            {isPercentage
              ? `${fmt(item.value)}%`
              : fmt(item.value)}
          </span>
        );
      })}
    </div>
  );
}


export default function App() {
  const [tab, setTab] =
    useState("overview");

  const [years, setYears] =
    useState<string[]>([]);

  const [fy, setFy] =
    useState("");

  const [overview, setOverview] =
    useState<Overview | null>(null);

  const [trends, setTrends] =
    useState<Trends | null>(null);

  const [error, setError] =
    useState("");

  const [refreshing, setRefreshing] =
    useState(false);

  const [fromDate, setFromDate] =
    useState("");

  const [toDate, setToDate] =
    useState("");

  const [theme, setTheme] =
    useState<"light" | "dark">(() => {
      const savedTheme =
        window.localStorage.getItem(
          "solar-dashboard-theme",
        );

      if (
        savedTheme === "light" ||
        savedTheme === "dark"
      ) {
        return savedTheme;
      }

      const prefersDarkMode =
        window.matchMedia(
          "(prefers-color-scheme: dark)",
        ).matches;

      return prefersDarkMode
        ? "dark"
        : "light";
    });


  useEffect(() => {
    document.documentElement.setAttribute(
      "data-theme",
      theme,
    );

    window.localStorage.setItem(
      "solar-dashboard-theme",
      theme,
    );
  }, [theme]);


  const load = async (
    value: string,
  ) => {
    const [
      overviewData,
      trendsData,
    ] = await Promise.all([
      api.get<Overview>(
        `/api/overview?fy=${encodeURIComponent(
          value,
        )}`,
      ),

      api.get<Trends>(
        `/api/trends?fy=${encodeURIComponent(
          value,
        )}`,
      ),
    ]);

    setOverview(overviewData);
    setTrends(trendsData);
  };


  useEffect(() => {
    api
      .get<{ items: string[] }>(
        "/api/financial-years",
      )
      .then((response) => {
        setYears(response.items);
        setFy(response.items[0] || "");
      })
      .catch((reason) => {
        setError(String(reason));
      });
  }, []);


  useEffect(() => {
    if (!fy) {
      return;
    }

    setError("");

    load(fy).catch((reason) => {
      setError(String(reason));
    });
  }, [fy]);
  


  async function refresh() {
    setRefreshing(true);
    setError("");

    try {
      const job = await api.post<any>(
        "/api/refresh",
      );

      const timer =
        window.setInterval(
          async () => {
            const status =
              await api.get<any>(
                `/api/refresh/${job.id}`,
              );

            if (
              status.status ===
                "completed" ||
              status.status ===
                "failed"
            ) {
              clearInterval(timer);
              setRefreshing(false);

              if (
                status.status ===
                "failed"
              ) {
                setError(status.error);
              } else {
                await load(fy);
              }
            }
          },
          1500,
        );
    } catch (reason) {
      setRefreshing(false);
      setError(String(reason));
    }
  }


  const trendDateBounds = useMemo(() => {
    const periods = (trends?.production ?? [])
      .map((row: any) => String(row.period ?? ""))
      .filter(Boolean)
      .sort();

    return {
      min: periods[0] ?? "",
      max: periods[periods.length - 1] ?? "",
    };
  }, [trends]);


  useEffect(() => {
    setFromDate(trendDateBounds.min);
    setToDate(trendDateBounds.max);
  }, [fy, trendDateBounds.min, trendDateBounds.max]);


  const inSelectedRange = (period: string) => {
    if (!period) {
      return false;
    }

    return (
      (!fromDate || period >= fromDate) &&
      (!toDate || period <= toDate)
    );
  };


  const filteredProduction = useMemo(
    () => (trends?.production ?? []).filter(
      (row: any) => inSelectedRange(String(row.period ?? "")),
    ),
    [trends, fromDate, toDate],
  );

  const filteredRejection = useMemo(
    () => (trends?.rejection ?? []).filter(
      (row: any) => inSelectedRange(String(row.period ?? "")),
    ),
    [trends, fromDate, toDate],
  );

  const filteredYield = useMemo(
    () => (trends?.yield ?? []).filter(
      (row: any) => inSelectedRange(String(row.period ?? "")),
    ),
    [trends, fromDate, toDate],
  );

  const filteredWaferLoss = useMemo(
    () => (trends?.wafer_loss ?? []).filter(
      (row: any) => inSelectedRange(String(row.period ?? "")),
    ),
    [trends, fromDate, toDate],
  );

  const filteredMonthlyAverage = useMemo(() => {
    const monthly = new Map<string, { total: number; count: number }>();

    for (const row of filteredProduction) {
      const month = String(row.period ?? "").slice(0, 7);
      if (!month) continue;

      const current = monthly.get(month) ?? { total: 0, count: 0 };
      current.total += Number(row.total_mw) || 0;
      current.count += 1;
      monthly.set(month, current);
    }

    return Array.from(monthly.entries()).map(([month, value]) => ({
      period: `${month}-01`,
      avg_mw_per_day: value.count ? value.total / value.count : 0,
    }));
  }, [filteredProduction]);


  const breakage = useMemo(() => {
    const fields = [
      "total_breakage",
      "rw_breakage",
      "bw_breakage",
      "alw_breakage",
      "agw_breakage",
      "cell_breakage",
    ];

    const labels: Record<string, string> = {
      total_breakage: "Total Breakage",
      rw_breakage: "R-W Breakage",
      bw_breakage: "B-W Breakage",
      alw_breakage: "AL-W Breakage",
      agw_breakage: "AG-W Breakage",
      cell_breakage: "Cell Breakage",
    };

    const dailyRows = (trends?.breakage_daily ?? []).filter(
      (row: any) => inSelectedRange(String(row.period ?? "")),
    );

    if (dailyRows.length) {
      return fields.map((field) => ({
        name: labels[field],
        value: dailyRows.reduce(
          (sum: number, row: any) => sum + (Number(row[field]) || 0),
          0,
        ),
      }));
    }

    return fields.map((field) => ({
      name: labels[field],
      value: Number(trends?.breakage?.[field]) || 0,
    }));
  }, [trends, fromDate, toDate]);


  return (
    <div className="app">
      <header>
        <img src="/company_logo.png" alt="Company logo" />

        <div className="brand">
          <h1>
            SOLAR MANUFACTURING DASHBOARD
          </h1>

          <p>
            Final Product · Production and
            Quality Intelligence
          </p>
        </div>

        <div className="controls">
          <label>
            Financial year

            <select
              value={fy}
              onChange={(event) =>
                setFy(event.target.value)
              }
            >
              {years.map((year) => (
                <option key={year}>
                  {year}
                </option>
              ))}
            </select>
          </label>

          {tab === "trends" && (
            <>
              <label>
                From date
                <input
                  type="date"
                  value={fromDate}
                  min={trendDateBounds.min}
                  max={toDate || trendDateBounds.max}
                  onChange={(event) => setFromDate(event.target.value)}
                  style={{
                    display: "block",
                    minWidth: 145,
                    marginTop: 5,
                    padding: "10px 11px",
                    color: "#17271f",
                    background: "#ffffff",
                    border: "1px solid #c9d9cb",
                    borderRadius: 10,
                  }}
                />
              </label>

              <label>
                To date
                <input
                  type="date"
                  value={toDate}
                  min={fromDate || trendDateBounds.min}
                  max={trendDateBounds.max}
                  onChange={(event) => setToDate(event.target.value)}
                  style={{
                    display: "block",
                    minWidth: 145,
                    marginTop: 5,
                    padding: "10px 11px",
                    color: "#17271f",
                    background: "#ffffff",
                    border: "1px solid #c9d9cb",
                    borderRadius: 10,
                  }}
                />
              </label>
            </>
          )}

          <div className="asof">
            AS OF
            <b>
              {overview?.as_of || "-"}
            </b>
          </div>
          <button
  type="button"
  className="themeToggle"
  onClick={() =>
    setTheme((currentTheme) =>
      currentTheme === "light"
        ? "dark"
        : "light",
    )
  }
  aria-label={
    theme === "light"
      ? "Switch to dark mode"
      : "Switch to light mode"
  }
  title={
    theme === "light"
      ? "Switch to dark mode"
      : "Switch to light mode"
  }
>
  {theme === "light" ? (
    <Moon />
  ) : (
    <Sun />
  )}

  <span>
    {theme === "light"
      ? "Dark"
      : "Light"}
  </span>
</button>
          <button
            onClick={refresh}
            disabled={refreshing}
          >
            <RefreshCw
              className={
                refreshing
                  ? "spin"
                  : ""
              }
            />

            {refreshing
              ? "Refreshing"
              : "Refresh SAP Data"}
          </button>
        </div>
      </header>


      {error && (
        <div className="error">
          {error}
        </div>
      )}


      <nav>
        <button
          className={
            tab === "overview"
              ? "active"
              : ""
          }
          onClick={() =>
            setTab("overview")
          }
        >
          Overview
        </button>

        <button
          className={
            tab === "trends"
              ? "active"
              : ""
          }
          onClick={() =>
            setTab("trends")
          }
        >
          Trends
        </button>
      </nav>


      <main>
        {tab === "overview" &&
          overview && (
            <>
              <div className="kpiGrid">
                {(overview.kpis ?? []).map(
                  (kpi) => (
                    <KpiCard
                      key={kpi.title}
                      k={kpi}
                    />
                  ),
                )}
              </div>


              <div
                className="floatingTableGrid"
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                  gap: 20,
                  alignItems: "stretch",
                  marginTop: 20,
                }}
              >
                <section
                  className="panel floatingTableCard"
                  style={{
                    marginTop: 0,
                    minWidth: 0,
                    height: "100%",
                    padding: 20,
                    display: "flex",
                    flexDirection: "column",
                    borderRadius: 18,
                    boxShadow: "0 12px 30px rgba(0, 74, 40, 0.10)",
                  }}
                >
                  <h2
                    style={{
                      margin: "4px 0 18px",
                      minHeight: 42,
                      color: "#10291c",
                      fontSize: "clamp(26px, 1.8vw, 34px)",
                      fontWeight: 900,
                      lineHeight: 1.15,
                      textAlign: "left",
                    }}
                  >
                    Production Distribution
                  </h2>
                  <div className="tableWrap" style={{ flex: 1 }}>
                    <table style={{ width: "100%", minWidth: 600, height: "100%", tableLayout: "fixed" }}>
                      <thead>
                        <tr>
                          <th style={{ width: "22%", fontSize: 13, padding: "14px 12px" }}>Grade / Type</th>
                          <th style={{ width: "20%", fontSize: 13, padding: "14px 12px" }}>Cells</th>
                          <th style={{ width: "18%", fontSize: 13, padding: "14px 12px" }}>On Date</th>
                          <th style={{ width: "20%", fontSize: 13, padding: "14px 12px" }}>MTD</th>
                          <th style={{ width: "20%", fontSize: 13, padding: "14px 12px" }}>YTD</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="group"><th colSpan={5} style={{ fontSize: 12, padding: "11px 12px" }}>Production</th></tr>
                        {(overview.distribution ?? []).map((row) => (
                          <tr key={row.label}>
                            <th style={{ fontSize: 15, padding: "14px 12px" }}>{row.label}</th>
                            <td style={{ fontSize: 14, fontWeight: 650, padding: "14px 12px" }}>{fmt(row.cells, 0)}</td>
                            <td style={{ fontSize: 14, fontWeight: 650, padding: "14px 12px" }}>{fmt(row.on_date)}</td>
                            <td style={{ fontSize: 14, fontWeight: 650, padding: "14px 12px" }}>{fmt(row.mtd)}</td>
                            <td style={{ fontSize: 14, fontWeight: 650, padding: "14px 12px" }}>{fmt(row.ytd)}</td>
                          </tr>
                        ))}
                        <tr className="group"><th colSpan={5} style={{ fontSize: 12, padding: "11px 12px" }}>Rejection</th></tr>
                        {(overview.rejection ?? []).map((row) => (
                          <tr key={row.label}>
                            <th style={{ fontSize: 15, padding: "14px 12px" }}>{row.label}</th>
                            <td style={{ fontSize: 14, fontWeight: 650, padding: "14px 12px" }}>{fmt(row.cells, 0)}</td>
                            <td style={{ fontSize: 14, fontWeight: 650, padding: "14px 12px" }}>{fmt(row.on_date, 0)}</td>
                            <td style={{ fontSize: 14, fontWeight: 650, padding: "14px 12px" }}>{fmt(row.mtd, 0)}</td>
                            <td style={{ fontSize: 14, fontWeight: 650, padding: "14px 12px" }}>{fmt(row.ytd, 0)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </section>

                <section
                  className="panel floatingTableCard"
                  style={{
                    marginTop: 0,
                    minWidth: 0,
                    height: "100%",
                    padding: 20,
                    display: "flex",
                    flexDirection: "column",
                    borderRadius: 18,
                    boxShadow: "0 12px 30px rgba(0, 74, 40, 0.10)",
                  }}
                >
                  <h2
                    style={{
                      margin: "4px 0 18px",
                      minHeight: 42,
                      color: "#10291c",
                      fontSize: "clamp(26px, 1.8vw, 34px)",
                      fontWeight: 900,
                      lineHeight: 1.15,
                      textAlign: "left",
                    }}
                  >
                    Yield % Distribution
                  </h2>
                  <div className="tableWrap" style={{ flex: 1 }}>
                    <table style={{ width: "100%", minWidth: 500, height: "100%", tableLayout: "fixed" }}>
                      <thead>
                        <tr>
                          <th style={{ width: "34%", fontSize: 13, padding: "14px 12px" }}>Grade / Type</th>
                          <th style={{ width: "22%", fontSize: 13, padding: "14px 12px" }}>On Date</th>
                          <th style={{ width: "22%", fontSize: 13, padding: "14px 12px" }}>MTD</th>
                          <th style={{ width: "22%", fontSize: 13, padding: "14px 12px" }}>YTD</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="group"><th colSpan={4} style={{ fontSize: 12, padding: "11px 12px" }}>Yield</th></tr>
                        {(overview.yield_table ?? []).map((row) => (
                          <tr key={row.label} className={row.label === "Good Cells" ? "total" : ""}>
                            <th style={{ fontSize: 15, padding: "14px 12px" }}>{row.label}</th>
                            <td style={{ fontSize: 14, fontWeight: 650, padding: "14px 12px" }}>{fmt(row.on_date)}%</td>
                            <td style={{ fontSize: 14, fontWeight: 650, padding: "14px 12px" }}>{fmt(row.mtd)}%</td>
                            <td style={{ fontSize: 14, fontWeight: 650, padding: "14px 12px" }}>{fmt(row.ytd)}%</td>
                          </tr>
                        ))}
                        <tr className="group"><th colSpan={4} style={{ fontSize: 12, padding: "11px 12px" }}>Rejection</th></tr>
                        {(overview.rejection_percentage_table ?? []).map((row) => (
                          <tr key={row.label} className={row.label === "Wafer Loss" ? "lossTotal" : ""}>
                            <th style={{ fontSize: 15, padding: "14px 12px" }}>{row.label}</th>
                            <td style={{ fontSize: 14, fontWeight: 650, padding: "14px 12px" }}>{fmt(row.on_date)}%</td>
                            <td style={{ fontSize: 14, fontWeight: 650, padding: "14px 12px" }}>{fmt(row.mtd)}%</td>
                            <td style={{ fontSize: 14, fontWeight: 650, padding: "14px 12px" }}>{fmt(row.ytd)}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </section>
              </div>
            </>
          )}


        {tab === "trends" &&
          trends && (
            <>
              <Chart
                title="Daywise Production Trend"
                subtitle="Total saleable cells with Overall MW and A Grade MW"
              >
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <ComposedChart
                    data={
                      filteredProduction
                    }
                    margin={{
                      top: 25,
                      right: 24,
                      left: 10,
                      bottom: 42,
                    }}
                  >
                    <CartesianGrid
                      stroke="#dfe7e1"
                      vertical={false}
                    />

                    <XAxis
                      {...axis}
                      dataKey="period"
                      tickFormatter={
                        shortDate
                      }
                      interval="preserveStartEnd"
                      minTickGap={40}
                      angle={-35}
                      textAnchor="end"
                      height={70}
                    />

                    <YAxis
                      {...axis}
                      yAxisId="cells"
                      tickFormatter={
                        cellTick
                      }
                      label={{
                        value:
                          "Production (Cells)",
                        angle: -90,
                        position:
                          "insideLeft",
                        fill: "#26352d",
                      }}
                    />

                    <YAxis
                      {...axis}
                      yAxisId="mw"
                      orientation="right"
                      domain={[
                        "auto",
                        "auto",
                      ]}
                      label={{
                        value:
                          "Production (MW)",
                        angle: 90,
                        position:
                          "insideRight",
                        fill: "#26352d",
                      }}
                    />

                    <Tooltip
                      content={
                        <TooltipBox />
                      }
                    />

                    <Legend
                      verticalAlign="top"
                      align="left"
                      wrapperStyle={{
                        paddingBottom: 14,
                      }}
                    />

                    <Bar
                      yAxisId="cells"
                      dataKey="total_cells"
                      fill="#62d4e8"
                      name="Total Saleable Cells"
                      radius={[
                        2,
                        2,
                        0,
                        0,
                      ]}
                    />

                    <Line
                      yAxisId="mw"
                      type="monotone"
                      dataKey="total_mw"
                      stroke="#23c875"
                      strokeWidth={2.5}
                      dot={false}
                      activeDot={{
                        r: 5,
                        fill: "#23c875",
                        stroke: "#ffffff",
                        strokeWidth: 2,
                      }}
                      name="Overall MW"
                      connectNulls
                    />

                    <Line
                      yAxisId="mw"
                      type="monotone"
                      dataKey="a_mw"
                      stroke="#2095f2"
                      strokeWidth={2.5}
                      dot={false}
                      activeDot={{
                        r: 5,
                        fill: "#2095f2",
                        stroke: "#ffffff",
                        strokeWidth: 2,
                      }}
                      name="A Grade MW"
                      connectNulls
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </Chart>


              <Chart
                title="Daywise Rejection Trend"
                subtitle="ER includes ER(Q); OR represents FOR"
              >
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <LineChart
                    data={
                      filteredRejection
                    }
                    margin={{
                      top: 25,
                      right: 30,
                      bottom: 48,
                      left: 8,
                    }}
                  >
                    <CartesianGrid
                      stroke="#e5ebe6"
                      vertical={false}
                    />

                    <XAxis
                      {...axis}
                      dataKey="period"
                      tickFormatter={
                        shortDate
                      }
                      interval="preserveStartEnd"
                      minTickGap={45}
                      angle={-35}
                      textAnchor="end"
                      height={72}
                      label={{
                        value:
                          "Production Date",
                        position:
                          "insideBottom",
                        offset: -17,
                        fill: "#43544a",
                        fontSize: 12,
                        fontWeight: 700,
                      }}
                    />

                    <YAxis
                      {...axis}
                      tickFormatter={
                        percentTick
                      }
                      domain={[
                        0,
                        (
                          dataMax: number,
                        ) =>
                          Math.max(
                            Math.ceil(
                              dataMax *
                                1.15,
                            ),
                            1,
                          ),
                      ]}
                      width={65}
                      label={{
                        value:
                          "Rejection (%)",
                        angle: -90,
                        position:
                          "insideLeft",
                        fill: "#43544a",
                        fontSize: 12,
                        fontWeight: 700,
                      }}
                    />

                    <Tooltip
                      content={
                        <TooltipBox />
                      }
                      cursor={{
                        stroke: "#b6c5ba",
                        strokeDasharray:
                          "4 4",
                      }}
                    />

                    <Legend
                      verticalAlign="top"
                      align="center"
                      iconType="circle"
                      iconSize={8}
                      wrapperStyle={{
                        paddingBottom: 15,
                        color: "#26352d",
                        fontSize: 12,
                        fontWeight: 700,
                      }}
                    />

                    <Line
                      type="monotone"
                      dataKey="breakage_pct"
                      name="Breakage %"
                      stroke="#f27a14"
                      strokeWidth={2.5}
                      dot={false}
                      activeDot={{
                        r: 5,
                        fill: "#f27a14",
                        stroke: "#ffffff",
                        strokeWidth: 2,
                      }}
                      connectNulls
                    />

                    <Line
                      type="monotone"
                      dataKey="er_pct"
                      name="ER %"
                      stroke="#60666b"
                      strokeWidth={2.5}
                      dot={false}
                      activeDot={{
                        r: 5,
                        fill: "#60666b",
                        stroke: "#ffffff",
                        strokeWidth: 2,
                      }}
                      connectNulls
                    />

                    <Line
                      type="monotone"
                      dataKey="or_pct"
                      name="OR %"
                      stroke="#438dcc"
                      strokeWidth={2.5}
                      dot={false}
                      activeDot={{
                        r: 5,
                        fill: "#438dcc",
                        stroke: "#ffffff",
                        strokeWidth: 2,
                      }}
                      connectNulls
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Chart>


              <Chart
                title="Yield Trend (%)"
                subtitle="Independent scales preserve visibility across all yield grades"
              >
                <div className="yieldSmallMultiples">
                  <div className="yieldSubChart yieldSubChartPrimary">
                    <div className="yieldScaleLabel">
                      <span className="yieldDot yieldDotAGrade" />
                      A Grade Yield
                    </div>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={filteredYield}
                        syncId="yield-trends"
                        margin={{ top: 12, right: 24, bottom: 0, left: 8 }}
                      >
                        <CartesianGrid stroke="#e5ebe6" vertical={false} />
                        <XAxis dataKey="period" hide />
                        <YAxis
                          {...axis}
                          width={62}
                          tickFormatter={percentTick}
                          domain={[
                            (dataMin: number) => Math.max(Math.floor(dataMin - 2), 0),
                            (dataMax: number) => Math.min(Math.ceil(dataMax + 2), 100),
                          ]}
                        />
                        <Tooltip
                          content={<TooltipBox />}
                          cursor={{ stroke: "#b6c5ba", strokeDasharray: "4 4" }}
                        />
                        <Line
                          type="monotone"
                          dataKey="a_yield_pct"
                          name="A Grade %"
                          stroke="#007a48"
                          strokeWidth={3}
                          dot={false}
                          activeDot={{ r: 5, fill: "#007a48", stroke: "#ffffff", strokeWidth: 2 }}
                          connectNulls
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="yieldSubChart yieldSubChartSecondary">
                    <div className="yieldScaleLabel">
                      <span className="yieldDot yieldDotBEL" />
                      B-EL Yield
                    </div>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={filteredYield}
                        syncId="yield-trends"
                        margin={{ top: 12, right: 24, bottom: 0, left: 8 }}
                      >
                        <CartesianGrid stroke="#e5ebe6" vertical={false} />
                        <XAxis dataKey="period" hide />
                        <YAxis
                          {...axis}
                          width={62}
                          tickFormatter={percentTick}
                          domain={[
                            0,
                            (dataMax: number) => Math.max(Math.ceil(dataMax * 1.1), 5),
                          ]}
                        />
                        <Tooltip
                          content={<TooltipBox />}
                          cursor={{ stroke: "#b6c5ba", strokeDasharray: "4 4" }}
                        />
                        <Line
                          type="monotone"
                          dataKey="bel_yield_pct"
                          name="B-EL %"
                          stroke="#f29419"
                          strokeWidth={2.7}
                          dot={false}
                          activeDot={{ r: 5, fill: "#f29419", stroke: "#ffffff", strokeWidth: 2 }}
                          connectNulls
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="yieldSubChart yieldSubChartSmall">
                    <div className="yieldScaleLabel">
                      <span className="yieldDot yieldDotBGrade" />
                      B Grade
                      <span className="yieldDot yieldDotEB" />
                      EB
                    </div>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={filteredYield}
                        syncId="yield-trends"
                        margin={{ top: 12, right: 24, bottom: 46, left: 8 }}
                      >
                        <CartesianGrid stroke="#e5ebe6" vertical={false} />
                        <XAxis
                          {...axis}
                          dataKey="period"
                          tickFormatter={shortDate}
                          interval="preserveStartEnd"
                          minTickGap={45}
                          angle={-35}
                          textAnchor="end"
                          height={64}
                        />
                        <YAxis
                          {...axis}
                          width={62}
                          tickFormatter={percentTick}
                          domain={[
                            0,
                            (dataMax: number) =>
                              Math.max(Math.ceil(dataMax * 1.2 * 10) / 10, 0.5),
                          ]}
                          allowDecimals
                        />
                        <Tooltip
                          content={<TooltipBox />}
                          cursor={{ stroke: "#b6c5ba", strokeDasharray: "4 4" }}
                        />
                        <Line
                          type="monotone"
                          dataKey="b_yield_pct"
                          name="B Grade %"
                          stroke="#258bd2"
                          strokeWidth={2.5}
                          dot={false}
                          activeDot={{ r: 5, fill: "#258bd2", stroke: "#ffffff", strokeWidth: 2 }}
                          connectNulls
                        />
                        <Line
                          type="monotone"
                          dataKey="eb_yield_pct"
                          name="EB %"
                          stroke="#7c5ac7"
                          strokeWidth={2.5}
                          dot={false}
                          activeDot={{ r: 5, fill: "#7c5ac7", stroke: "#ffffff", strokeWidth: 2 }}
                          connectNulls
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </Chart>


              <Chart
                title="Wafer Loss Trend (%)"
                subtitle="ER + OR + Breakage"
              >
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <LineChart
                    data={
                      filteredWaferLoss
                    }
                    margin={{
                      top: 28,
                      right: 24,
                      left: 8,
                      bottom: 48,
                    }}
                  >
                    <CartesianGrid
                      stroke="#e3e9e4"
                      vertical={false}
                    />

                    <XAxis
                      {...axis}
                      dataKey="period"
                      tickFormatter={
                        shortDate
                      }
                      interval="preserveStartEnd"
                      minTickGap={45}
                      angle={-35}
                      textAnchor="end"
                      height={72}
                    />

                    <YAxis
                      {...axis}
                      domain={[
                        0,
                        (
                          dataMax: number,
                        ) =>
                          Math.max(
                            Math.ceil(
                              dataMax *
                                1.15,
                            ),
                            1,
                          ),
                      ]}
                      tickFormatter={
                        percentTick
                      }
                    />

                    <Tooltip
                      content={
                        <TooltipBox />
                      }
                    />

                    <Legend />

                    <Line
                      type="monotone"
                      dataKey="wafer_loss_pct"
                      stroke="#d84c5b"
                      strokeWidth={3}
                      dot={false}
                      activeDot={{
                        r: 5,
                        fill: "#d84c5b",
                        stroke: "#ffffff",
                        strokeWidth: 2,
                      }}
                      name="Wafer Loss %"
                      connectNulls
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Chart>


              <Chart title="Breakage Distribution">
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <BarChart
                    data={breakage}
                    margin={{
                      top: 30,
                      right: 20,
                      left: 8,
                      bottom: 50,
                    }}
                  >
                    <CartesianGrid
                      stroke="#e3e9e4"
                      vertical={false}
                    />

                    <XAxis
                      {...axis}
                      dataKey="name"
                      interval={0}
                      angle={-25}
                      textAnchor="end"
                      height={68}
                    />

                    <YAxis
                      {...axis}
                      tickFormatter={
                        cellTick
                      }
                    />

                    <Tooltip
                      content={
                        <TooltipBox />
                      }
                    />

                    <Bar
                      dataKey="value"
                      fill="#79c143"
                      name="Breakage Cells"
                      radius={[
                        6,
                        6,
                        0,
                        0,
                      ]}
                    >
                      <LabelList
                        dataKey="value"
                        position="top"
                        formatter={(
                          value: any,
                        ) =>
                          fmt(value, 0)
                        }
                        fill="#26352d"
                        fontSize={10}
                      />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Chart>


              <Chart title="Monthly Average MW Production per Day">
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <LineChart
                    data={
                      filteredMonthlyAverage
                    }
                    margin={{
                      top: 28,
                      right: 24,
                      left: 8,
                      bottom: 32,
                    }}
                  >
                    <CartesianGrid
                      stroke="#e3e9e4"
                      vertical={false}
                    />

                    <XAxis
                      {...axis}
                      dataKey="period"
                      tickFormatter={
                        monthLabel
                      }
                    />

                    <YAxis
                      {...axis}
                      domain={[
                        "auto",
                        "auto",
                      ]}
                      label={{
                        value:
                          "Average MW/day",
                        angle: -90,
                        position:
                          "insideLeft",
                        fill: "#26352d",
                      }}
                    />

                    <Tooltip
                      content={
                        <TooltipBox />
                      }
                    />

                    <Legend />

                    <Line
                      type="monotone"
                      dataKey="avg_mw_per_day"
                      stroke="#006b3f"
                      strokeWidth={3}
                      dot={{
                        r: 5,
                        fill: "#79c143",
                        stroke: "#006b3f",
                      }}
                      activeDot={{
                        r: 6,
                        fill: "#006b3f",
                        stroke: "#ffffff",
                        strokeWidth: 2,
                      }}
                      name="Average MW/day"
                    >
                      <LabelList
                        dataKey="avg_mw_per_day"
                        position="top"
                        formatter={(
                          value: any,
                        ) =>
                          fmt(value, 2)
                        }
                        fill="#006b3f"
                        fontSize={10}
                      />
                    </Line>
                  </LineChart>
                </ResponsiveContainer>
              </Chart>
            </>
          )}
      </main>
    </div>
  );
}