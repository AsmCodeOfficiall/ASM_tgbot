import { formatUsd } from "../utils/format";
import { tg } from "../utils/theme";

const TYPE_LABELS = {
  fund: "У фонд",
  credit: "Нарахування",
};

function formatDate(iso) {
  if (!iso) return "";
  try {
    return new Intl.DateTimeFormat("uk-UA", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(iso));
  } catch {
    return "";
  }
}

const TransactionList = ({ transactions = [] }) => {
  return (
    <section
      className="p-5 rounded-2xl flex-1 min-h-0"
      style={{
        backgroundColor: tg.sectionBg,
        border: `1px solid ${tg.hint}`,
      }}
    >
      <h2 className="text-sm font-medium mb-3" style={{ color: tg.hint }}>
        Останні транзакції / проєкти
      </h2>

      {!transactions.length ? (
        <p className="text-sm" style={{ color: tg.hint }}>
          Поки що немає операцій
        </p>
      ) : (
        <ul className="flex flex-col gap-1 max-h-48 overflow-y-auto">
          {transactions.map((tx) => (
            <li
              key={tx.id}
              className="flex justify-between items-center gap-3 py-2.5 border-b last:border-0"
              style={{ borderColor: tg.secondaryBg }}
            >
              <div className="min-w-0 flex-1">
                <p className="font-medium truncate">
                  {tx.project_name || TYPE_LABELS[tx.type] || tx.type}
                </p>
                <p className="text-xs truncate" style={{ color: tg.hint }}>
                  {TYPE_LABELS[tx.type] || tx.type}
                  {tx.created_at ? ` · ${formatDate(tx.created_at)}` : ""}
                </p>
              </div>
              <span
                className="shrink-0 tabular-nums font-semibold"
                style={{
                  color: tx.type === "credit" ? tg.link : tg.text,
                }}
              >
                {tx.type === "credit" ? "+" : ""}
                {formatUsd(tx.value)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
};

export default TransactionList;
