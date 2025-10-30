// Мок-данные для CRM системы

export interface Building {
  id: string;
  type: 'МКД' | 'Бизнес-центр' | 'ТЦ' | 'Школа' | 'Больница';
  address: string;
  city: string;
  district: string;
  status: 'Новый' | 'В работе' | 'Ожидание' | 'Завершён' | 'Отказ';
  visitsCount: number;
  lastVisit: string;
  responsible: string;
  gps?: { lat: number; lng: number };
  apartmentsCount?: number;
}

export interface Visit {
  id: string;
  date: string;
  engineer: string;
  building: string;
  apartment?: string;
  status: 'Завершён' | 'В процессе' | 'Отменён' | 'Запланирован';
  interest: string[];
  nextAction?: string;
  notes?: string;
}

export interface Customer {
  id: string;
  name: string;
  phone: string;
  building: string;
  apartment: string;
  currentProvider?: string;
  rating?: number;
  interests: string[];
  convenientTime?: string;
  desiredPrice?: string;
  updatedAt: string;
}

export interface User {
  id: string;
  name: string;
  role: 'Инженер' | 'Супервайзер' | 'Админ';
  city: string;
  zone?: string;
  lastLogin: string;
  isActive: boolean;
}

export const mockBuildings: Building[] = [
  {
    id: '1',
    type: 'МКД',
    address: 'ул. Пушкина, д. 12',
    city: 'Москва',
    district: 'Центральный',
    status: 'В работе',
    visitsCount: 45,
    lastVisit: '2025-10-28',
    responsible: 'Иванов И.И.',
    apartmentsCount: 120,
    gps: { lat: 55.7558, lng: 37.6173 }
  },
  {
    id: '2',
    type: 'Бизнес-центр',
    address: 'пр-т Ленина, д. 50',
    city: 'Москва',
    district: 'Северный',
    status: 'Новый',
    visitsCount: 0,
    lastVisit: '-',
    responsible: 'Петров П.П.',
    apartmentsCount: 80,
    gps: { lat: 55.7658, lng: 37.6273 }
  },
  {
    id: '3',
    type: 'ТЦ',
    address: 'Торговый комплекс "Галерея"',
    city: 'Санкт-Петербург',
    district: 'Приморский',
    status: 'Завершён',
    visitsCount: 120,
    lastVisit: '2025-10-25',
    responsible: 'Сидоров С.С.',
    apartmentsCount: 200,
    gps: { lat: 59.9342, lng: 30.3350 }
  },
  {
    id: '4',
    type: 'МКД',
    address: 'ул. Гагарина, д. 8',
    city: 'Москва',
    district: 'Южный',
    status: 'Ожидание',
    visitsCount: 15,
    lastVisit: '2025-10-20',
    responsible: 'Иванов И.И.',
    apartmentsCount: 90,
    gps: { lat: 55.7458, lng: 37.6073 }
  },
  {
    id: '5',
    type: 'Школа',
    address: 'Школа №42',
    city: 'Москва',
    district: 'Восточный',
    status: 'Отказ',
    visitsCount: 3,
    lastVisit: '2025-10-15',
    responsible: 'Петров П.П.',
    gps: { lat: 55.7858, lng: 37.6473 }
  }
];

export const mockVisits: Visit[] = [
  {
    id: '1',
    date: '2025-10-28 14:30',
    engineer: 'Иванов И.И.',
    building: 'ул. Пушкина, д. 12',
    apartment: '45',
    status: 'Завершён',
    interest: ['Интернет', 'ТВ'],
    nextAction: '2025-11-05',
    notes: 'Клиент заинтересован в подключении'
  },
  {
    id: '2',
    date: '2025-10-28 10:00',
    engineer: 'Иванов И.И.',
    building: 'ул. Пушкина, д. 12',
    apartment: '12',
    status: 'Завершён',
    interest: ['Видеонаблюдение'],
    notes: 'Требуется консультация по тарифам'
  },
  {
    id: '3',
    date: '2025-10-29 09:00',
    engineer: 'Петров П.П.',
    building: 'пр-т Ленина, д. 50',
    status: 'Запланирован',
    interest: [],
  },
  {
    id: '4',
    date: '2025-10-27 16:00',
    engineer: 'Сидоров С.С.',
    building: 'Торговый комплекс "Галерея"',
    apartment: 'Офис 301',
    status: 'Завершён',
    interest: ['Интернет', 'Видеонаблюдение'],
    nextAction: '2025-11-10'
  }
];

export const mockCustomers: Customer[] = [
  {
    id: '1',
    name: 'Алексей Смирнов',
    phone: '+7 (912) 345-67-89',
    building: 'ул. Пушкина, д. 12',
    apartment: '45',
    currentProvider: 'Конкурент А',
    rating: 3,
    interests: ['Интернет', 'ТВ'],
    convenientTime: '18:00-20:00',
    desiredPrice: '800 руб/мес',
    updatedAt: '2025-10-28'
  },
  {
    id: '2',
    name: 'Мария Петрова',
    phone: '+7 (905) 123-45-67',
    building: 'ул. Пушкина, д. 12',
    apartment: '12',
    currentProvider: 'Конкурент Б',
    rating: 2,
    interests: ['Видеонаблюдение'],
    convenientTime: '14:00-16:00',
    desiredPrice: '500 руб/мес',
    updatedAt: '2025-10-28'
  },
  {
    id: '3',
    name: 'Иван Козлов',
    phone: '+7 (916) 789-01-23',
    building: 'ул. Гагарина, д. 8',
    apartment: '78',
    rating: 5,
    interests: ['Интернет', 'ТВ', 'Интернет-няня'],
    convenientTime: 'Любое',
    desiredPrice: '1200 руб/мес',
    updatedAt: '2025-10-27'
  }
];

export const mockUsers: User[] = [
  {
    id: '1',
    name: 'Иванов Иван Иванович',
    role: 'Инженер',
    city: 'Москва',
    zone: 'Центральный',
    lastLogin: '2025-10-28 15:30',
    isActive: true
  },
  {
    id: '2',
    name: 'Петров Пётр Петрович',
    role: 'Инженер',
    city: 'Москва',
    zone: 'Северный',
    lastLogin: '2025-10-28 14:20',
    isActive: true
  },
  {
    id: '3',
    name: 'Сидоров Сергей Сергеевич',
    role: 'Супервайзер',
    city: 'Санкт-Петербург',
    zone: 'Приморский',
    lastLogin: '2025-10-27 18:45',
    isActive: true
  },
  {
    id: '4',
    name: 'Админов Админ Админович',
    role: 'Админ',
    city: 'Москва',
    zone: '-',
    lastLogin: '2025-10-28 09:00',
    isActive: true
  }
];

export const cities = ['Москва', 'Санкт-Петербург', 'Екатеринбург', 'Казань'];
export const districts = ['Центральный', 'Северный', 'Южный', 'Восточный', 'Западный', 'Приморский'];
export const buildingTypes = ['МКД', 'Бизнес-центр', 'ТЦ', 'Школа', 'Больница'];
export const statuses = ['Новый', 'В работе', 'Ожидание', 'Завершён', 'Отказ'];
export const services = ['Интернет', 'ТВ', 'Видеонаблюдение', 'Интернет-няня'];
