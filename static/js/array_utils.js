Array.each = function(a, fn){
	for(var i=0; i <a.length; i++){
		fn(a[i]);
	}
};
Array.prototype.each = function(fn){
	Array.each(this,fn);
};
Array.collect = function(a, fn){
	var new_array = new Array();
	a.each(function(e){
		new_array.push(fn(e));
	});
	return new_array;
};
Array.prototype.collect = function(fn){
	return Array.collect(this, fn);
};
Array.inject = function(a, init, fn){
	a.each(function(e){
		init = fn(init, e);
	});
	return init;
};
Array.prototype.inject = function(init, fn){
	return Array.inject(this, init, fn);
};
Array.detect = function(a, fn){
	for(var i=0; i <a.length; i++){
		if(fn(a[i])){
			return a[i];
		}
	}
};
Array.prototype.detect = function(fn){
	return Array.detect(this, fn);
};
Array.select = function(a, fn){
	var new_array = new Array();
	a.each(function(e){
		if(fn(e)){
			new_array.push(e);
		}
	});
	return new_array;
};
Array.prototype.select = function(fn){
	return Array.select(this, fn);
};
Array.reject = function(a, fn){
	return a.select(function(e){
		return (!fn(e));
	});
};
Array.prototype.reject = function(fn){
	return Array.reject(this,fn);
};
Array.reduce = Array.inject;
Array.prototype.reduce = Array.prototype.inject;
Array.map = Array.collect;
Array.prototype.map = Array.prototype.collect;