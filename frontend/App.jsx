// Ishak: один екран — фонд, баланс, список; відкриває модалку нового проєкту

import Dashboard from "./components/dashboard";

//1 память для данных бэкенда
const [data, setData] = useState({ fund: 0, balance: 0, transactions: [] });

//2 память для крутилки загрузки
const [isLoading, setIsLoading] = useState(true);

//3 память для модельного окна проекта
const [isModalOpen, setIsModalOpen] = useState(false);

//функция которая берет данные из бэкенда
const loadDashboard = async () => {   //async нужен что бы функция не зависала и не блокировала интерфейс пока ждет ответа от бэкенда
    setIsLoading(true);
    //если получаем данные из бэкенда:
    try {
        
        setData(result);
    } catch (error) {
    console.error('Error loading dashboard:', error);
    } finally {
        setIsLoading(false);
    }
        
};

//при старте вызываем функцию загрузки данных
useEffect(() => {    //useEffect нужен что бы вызвать функцию загрузки данных при старте
    loadDashboard();
}, []);   // пустой массив означает что функция загрузки данных будет вызвана только при старте


const handleOpenModal = () => setIsModalOpen(true);

const handleCloseModal = () => setIsModalOpen(false); 

return (
    <div className = "p-4 min-h-screen flex flex-col gap-4">

        {isLoading ? (
            <div className = "flex justify-center items-center h-40">
                <span className = "text-gray-500">Завантаження...</span>
            </div>
        ) : (
            <>
                <Dashboard fund = {data.fund} balance = {data.balance} />

                <button onClick = {handleOpenModal} className = "w-full bg-blue-500 text-white font-semibold py-3 px-4 rounded-xl active:bg-blue-600 transition-colors">
                    Додати проєкт
                </button>
                <TransactionList transactions = {data.transactions} />
            </>
        )}

        {isModalOpen && (<ProjectModal onClose = {handleCloseModal} onSuccess = {loadDashboard} />)}

        </div>
);


