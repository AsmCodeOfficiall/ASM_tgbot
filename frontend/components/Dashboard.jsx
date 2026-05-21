import { formatUsd } from "../utils/format";
import { tg } from "../utils/theme";

const Dashboard = ({ fund, balance }) => {
  return (
    <div className="flex flex-col gap-3">
      <section
        className="p-5 rounded-2xl"
        style={{ backgroundColor: tg.secondaryBg }}
      >
        <h2 className="text-sm font-medium" style={{ color: tg.hint }}>
          Загальний фонд команди
        </h2>
        <p className="text-3xl font-bold mt-1 tabular-nums">{formatUsd(fund)}</p>
      </section>

      <section
        className="p-5 rounded-2xl"
        style={{
          backgroundColor: tg.sectionBg,
          border: `1px solid ${tg.hint}`,
        }}
      >
        <h2 className="text-sm font-medium" style={{ color: tg.link }}>
          Особистий баланс
        </h2>
        <p
          className="text-3xl font-bold mt-1 tabular-nums"
          style={{ color: tg.accent }}
        >
          {formatUsd(balance)}
        </p>
      </section>
    </div>
  );
};

export default Dashboard;
