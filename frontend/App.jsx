// Ishak: один екран — фонд, баланс, список; відкриває модалку нового проєкту

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
    // тут кароче написать шото шо будет в интерфейсе


