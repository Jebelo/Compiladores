program PruebaLexer;

{ Declaración de variables }
var
 // 2edad : Integer; ejemplo que tiene que dar error ya que un ID no puede ser primero con numero
  edad : Integer;
  precio : Float;
  contador, total : Integer;
  nombre : String;
  activo : Boolean;
  y : Integer;
  z : Integer;
  Fibonacci : Integer;
  i: Integer; //Integer - integer
  PI : Float;

(* Inicio del programa *)
begin

  edad := hola; // Incompatibilidad de variables
  precio := 19.99;
  contador := 0;
  total := 10;
  caracter := 'A';
  x := 200; // Variable no declarada
  y := nombre + total; // Variable con operacion invalida
  z := 5 / 0; //Division incorrecta
  PI := 5; // Constante que no se puede cambiar

  // ciclo while
  while contador < total do
  begin
    contador := contador + 1;
  end;

  // condicional
  if edad >= 18 then
  begin
    activo := 1;
  end
  else
  begin
    activo := 0;
  end;

  // ciclo for
  for contador := 1 to 5 do
  begin
    total := total + contador;
  end;

  // repeat until
  repeat
    contador := contador - 1;
  until contador = 0;

end.